## 使用标记器 API {#sec:MarkerAPI}

在某些情况下，我们可能对分析特定代码区域的性能感兴趣，而不是整个应用程序。例如，当您开发一段新代码并只想关注该代码时，就会遇到这种情况。自然地，您会希望跟踪优化进度并捕获其他性能数据，以帮助您一路前进。大多数性能分析工具都提供特定的 *标记器 API*，可以让您做到这一点。这里有一些例子：

* Likwid 有 `LIKWID_MARKER_START / LIKWID_MARKER_STOP` 宏。
* Intel VTune 有 `__itt_task_begin / __itt_task_end` 函数。
* AMD uProf 有 `amdProfileResume / amdProfilePause` 函数。

这种混合方法结合了检测和性能事件计数的优点。标记器 API 允许我们将性能统计数据归因于代码区域（循环、函数）或功能片段（远程过程调用 (RPC)、输入事件等），而不是测量整个程序。您获得的数据质量足以证明这种努力是值得的。例如，在追查仅针对特定类型 RPC 出现的性能漏洞时，您可以仅针对该类型的 RPC 启用监控。

下面我们提供了一个非常基本的示例，展示了如何使用  [libpfm4](https://sourceforge.net/p/perfmon2/libpfm4/ci/master/tree/)[^1]，这是一个流行的用于收集性能监控事件的 Linux 库。它构建在 Linux `perf_events` 子系统之上，该子系统允许您直接访问性能事件计数器。`perf_events` 子系统相当底层，因此 `libfm4` 包在这里很有用，因为它增加了用于识别 CPU 上可用事件的发现工具以及围绕原始 `perf_event_open` 系统调用的包装库。[@lst:LibpfmMarkerAPI] 展示了如何使用 `libpfm4` 为 [C-Ray](https://openbenchmarking.org/test/pts/c-ray)[^2] benchmark 的 `render` 函数进行检测。

代码清单：在 C-Ray benchmark 上使用 libpfm4 标记器 API {#lst:LibpfmMarkerAPI}

```cpp 
+#include <perfmon/pfmlib.h>
+#include <perfmon/pfmlib_perf_event.h>
...
/* render a frame of xsz/ysz dimensions into the provided framebuffer */
void render(int xsz, int ysz, uint32_t *fb, int samples) {
   ...
+  pfm_initialize();
+  struct perf_event_attr perf_attr;
+  memset(&perf_attr, 0, sizeof(perf_attr));
+  perf_attr.size = sizeof(struct perf_event_attr);
+  perf_attr.read_format = PERF_FORMAT_TOTAL_TIME_ENABLED | 
+                          PERF_FORMAT_TOTAL_TIME_RUNNING | PERF_FORMAT_GROUP;
+   
+  pfm_perf_encode_arg_t arg;
+  memset(&arg, 0, sizeof(pfm_perf_encode_arg_t));
+  arg.size = sizeof(pfm_perf_encode_arg_t);
+  arg.attr = &perf_attr;
+   
+  pfm_get_os_event_encoding("instructions", PFM_PLM3, PFM_OS_PERF_EVENT_EXT, &arg);
+  int leader_fd = perf_event_open(&perf_attr, 0, -1, -1, 0);
+  pfm_get_os_event_encoding("cycles", PFM_PLM3, PFM_OS_PERF_EVENT_EXT, &arg);
+  int event_fd = perf_event_open(&perf_attr, 0, -1, leader_fd, 0);
+  pfm_get_os_event_encoding("branches", PFM_PLM3, PFM_OS_PERF_EVENT_EXT, &arg);
+  event_fd = perf_event_open(&perf_attr, 0, -1, leader_fd, 0);
+  pfm_get_os_event_encoding("branch-misses", PFM_PLM3, PFM_OS_PERF_EVENT_EXT, &arg);
+  event_fd = perf_event_open(&perf_attr, 0, -1, leader_fd, 0);
+
+  struct read_format { uint64_t nr, time_enabled, time_running, values[4]; };
+  struct read_format before, after;

  for(j=0; j<ysz; j++) {
    for(i=0; i<xsz; i++) {
      double r = 0.0, g = 0.0, b = 0.0;
+     // capture counters before ray tracing
+     read(event_fd, &before, sizeof(struct read_format));

      for(s=0; s<samples; s++) {
        struct vec3 col = trace(get_primary_ray(i, j, s), 0);
        r += col.x;
        g += col.y;
        b += col.z;
      }
+     // capture counters after ray tracing
+     read(event_fd, &after, sizeof(struct read_format));

+     // save deltas in separate arrays
+     nanosecs[j * xsz + i] = after.time_running - before.time_running;
+     instrs  [j * xsz + i] = after.values[0] - before.values[0];
+     cycles  [j * xsz + i] = after.values[1] - before.values[1];
+     branches[j * xsz + i] = after.values[2] - before.values[2];
+     br_misps[j * xsz + i] = after.values[3] - before.values[3];

      *fb++ = ((uint32_t)(MIN(r * rcp_samples, 1.0) * 255.0) & 0xff) << RSHIFT |
              ((uint32_t)(MIN(g * rcp_samples, 1.0) * 255.0) & 0xff) << GSHIFT |
              ((uint32_t)(MIN(b * rcp_samples, 1.0) * 255.0) & 0xff) << BSHIFT;
  } }
+ // aggregate statistics and print it
  ...
}
```

在这个代码示例中，我们首先初始化`libpfm`库并配置性能事件以及我们将用于读取它们的格式。在C-Ray基准测试中，`render`函数只被调用一次。在您自己的代码中，务必小心不要多次进行`libpfm`初始化。然后，我们选择要分析的代码区域，在我们的案例中，它是一个带有`trace`函数调用的循环。我们用两个`read`系统调用包围这个代码区域，它们将在循环之前和之后捕获性能计数器的值。接下来，我们保存这些增量以供以后处理，例如，在这种情况下，我们通过计算平均值、90th百分位数和最大值对其进行了聚合（代码未显示）。在基于Intel Alderlake的机器上运行它，我们得到了下面显示的输出。不需要root权限，但`/proc/sys/kernel/perf_event_paranoid`应该设置为小于1。当在一个线程内读取计数器时，这些值仅适用于该线程。它可以选择性地包括运行并归因于该线程的内核代码。

```bash
$ ./c-ray-f -s 1024x768 -r 2 -i sphfract -o output.ppm
Per-pixel ray tracing stats:
                      avg         p90         max
-------------------------------------------------
nanoseconds   |      4571 |      6139 |     25567
instructions  |     71927 |     96172 |    165608
cycles        |     20474 |     27837 |    118921
branches      |      5283 |      7061 |     12149
branch-misses |        18 |        35 |       146
```

请记住，我们添加的仪器测量了每个像素的光线跟踪统计数据。将平均数乘以像素数（`1024x768`）应该给出大致的程序总统计数据。在这种情况下，一个很好的健全性检查是运行`perf stat`并比较我们收集的性能事件的整体C-Ray统计数据。

C-ray基准测试主要强调CPU核心的浮点性能，通常不应该导致测量结果的高方差，换句话说，我们期望所有的测量结果都非常接近。然而，我们看到情况并非如此，因为p90值是平均值的1.33倍，而最大值有时比平均情况慢5倍。这里最可能的解释是对于一些像素，算法遇到了一个边界情况，执行了更多的指令，随后运行时间更长。但最好通过研究源代码或扩展仪器测量来捕获更多有关“慢”像素的数据，以确认假设。

[@lst:LibpfmMarkerAPI]中显示的附加仪器测量代码导致了17%的开销，这对于本地实验来说是可以接受的，但在生产环境中运行的开销相当高。大多数大型分布式系统的目标是小于1%的开销，对于某些系统来说，最多可接受5%的开销，但是17%的减速不太可能让用户满意。管理仪器测量的开销至关重要，特别是如果您选择在生产环境中启用它。

开销通常以时间单位或工作单位（RPC、数据库查询、循环迭代等）的发生率来计算。如果我们系统上的一个系统调用大约需要1.6微秒的CPU时间，并且我们每个像素都执行两次（外部循环的迭代），那么每个像素的开销就是3.2微秒的CPU时间。

降低开销的策略有很多。作为一个通用原则，您的仪器测量应该始终具有固定的成本，例如，确定性系统调用，但不是列表遍历或动态内存分配，否则它会干扰测量。仪器测量代码有三个逻辑部分：收集信息、存储信息和报告信息。为了降低第一部分（收集）的开销，我们可以减少采样率，例如，每10个RPC采样一次，然后跳过其余的。对于长时间运行的应用程序，性能可以通过相对便宜的随机采样进行监视 - 随机选择要观察的事件。这些方法牺牲了收集的准确性，但仍然提供了对整体性能特征的良好估计，同时产生了非常低的开销。

对于第二部分和第三部分（存储和聚合），建议仅收集、处理和保留您需要了解系统性能的数据量。您可以通过使用“在线”算法来计算平均值、方差、最小值、最大值和其他指标来避免将每个样本存储在内存中。这将大大减少仪器测量的内存占用。例如，方差和标准差可以使用Knuth的在线方差算法来计算。一个良好的实现[^3]使用不到50字节的内存。

对于长时间运行的例程，您可以在开始、结束和一些中间部分收集计数器。在连续运行中，您可以二分搜索执行最差的例程部分并进行优化。重复此过程，直到所有性能差的地方都被消除。如果尾延迟是主要关注的问题，那么在特别慢的运行中发出日志消息可以提供有用的见解。

在[@lst:LibpfmMarkerAPI]中，我们同时收集了4个事件，尽管CPU有6个可编程计数器。您可以打开具有不同事件集的其他组。内核将选择不同的组来运行。`time_enabled`和`time_running`字段指示了多路复用。它们都是以纳秒为单位的持续时间。`time_enabled`字段表示事件组已启用的纳秒数。`time_running`表示实际收集事件的时间占已启用时间的多少。如果同时启用了两个无法放在HW计数器上的事件组，您可能会看到它们都收敛到`time_running = 0.5 * time_enabled`。调度通常很复杂，因此在依赖于您的确切场景之前，请进行验证。

同时捕获多个事件允许计算我们在第4章中讨论的各种指标。例如，捕获`INSTRUCTIONS_RETIRED`和`UNHALTED_CLOCK_CYCLES`使我们能够测量IPC。我们可以通过比较CPU周期（`UNHALTED_CORE_CYCLES`）和固定频率参考时钟（`UNHALTED_REFERENCE_CYCLES`）来观察频率缩放的影响。通过请求消耗的CPU周期（`UNHALTED_CORE_CYCLES`，仅在线程运行时计数）并与墙钟时间进行比较，可以检测线程未运行的情况。此外，我们可以对数字进行归一化，以获得每秒/时钟/指令的事件速率。例如，通过测量`MEM_LOAD_RETIRED.L3_MISS`和`INSTRUCTIONS_RETIRED`，我们可以获得`L3MPKI`指标。正如您所见，这种设置非常灵活。

事件分组的重要属性是计数器将原子地在同一次`read`系统调用下可用。这些原子束非常有用。首先，它允许我们在每个组内相关事件。例如，我们为代码区域测量IPC，并发现它非常低。在这种情况下，我们可以将两个事件（指令和周期）与第三个事件配对，例如L3缓存丢失，以检查它是否对我们正在处理的低IPC有贡献。如果没有，我们将继续使用其他事件进行因子分析。其次，事件分组有助于减轻工作负载具有不同阶段的偏差。由于组内的所有事件同时测量，它们始终捕获相同的阶段。

在某些场景中，仪器测量可能成为功能或特性的一部分。例如，开发人员可以实现一个仪器测量逻辑，用于检测IPC的下降（例如，当有一个繁忙的兄弟硬件线程运行时）或CPU频率的下降（例如，由于负载过重而导致系统节流）。当发生这种事件时，应用程序会自动推迟低优先级的工作以补偿临时增加的负载。

[^1]: libpfm4 - [https://sourceforge.net/p/perfmon2/libpfm4/ci/master/tree/](https://sourceforge.net/p/perfmon2/libpfm4/ci/master/tree/)

[^2]: C-Ray基准测试 - [https://openbenchmarking.org/test/pts/c-ray](https://openbenchmarking.org/test/pts/c-ray)

[^3]: 准确计算运行方差 - [https://www.johndcook.com/blog/standard_deviation/](https://www.johndcook.com/blog/standard_deviation/)
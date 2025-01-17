## 低延迟优化技术 {#sec:LowLatency}

到目前为止，我们已经讨论了各种旨在改进应用程序整体性能的软件优化。在这一节中，我们将讨论在低延迟系统（例如实时处理和高频交易 (HFT)）中使用的额外优化技术。在这样的环境中，主要的优化目标是使程序的特定部分尽可能快地运行。当您在 HFT 行业工作时，每个微秒和纳秒都至关重要，因为它直接影响利润。通常，低延迟部分会实现实时或 HFT 系统的关键循环，例如移动机械臂或向交易所发送订单。优化关键路径的延迟有时会以牺牲程序其他部分为代价。一些技术甚至会牺牲整个系统的整体吞吐量。

当开发人员优化延迟时，他们会避免在热点路径上支付任何不必要的开销。这通常涉及系统调用、内存分配、I/O 以及任何其他具有非确定性延迟的内容。为了达到最低可能的延迟，热点路径需要提前准备好所有资源并可供其使用。

一个相对简单的方法是预先计算一些会在热点路径上执行的操作。这会带来使用更多内存的代价，这些内存将无法供系统中的其他进程使用，但它可以为您在关键路径上节省一些宝贵的周期。但是，请记住，有时计算内容比从内存中获取结果更快。

既然这是一本关于低级 CPU 性能的书籍，我们将跳过讨论类似于刚才提到的更高层次的技术。相反，我们将讨论如何在关键路径上避免页面错误、缓存未命中、TLB 驱逐和核心节流。

### 避免小页面错误 {#sec:AvoidPageFaults}

虽然“小”这个词存在，但小页面错误对运行时延迟的影响并不小。回想一下，当用户代码分配内存时，操作系统只会承诺提供一个页面，但不会立即通过提供一个已清零的物理页面来执行承诺。相反，它会等到用户代码第一次访问它时，然后操作系统才会履行其职责。第一次访问新分配的页面会触发小页面错误，这是一个由操作系统处理的硬件中断。小错误的延迟影响可以从不到 1 微秒到几微秒，尤其是在您使用具有 5 层页表而不是 4 层页表的 Linux 内核时。

如何检测应用程序中运行时的小页面错误？一种简单的方法是使用 `top` 实用程序（添加 `-H` 选项以查看线程级别视图）。将 `vMn` 字段添加到默认的显示列选择中，以查看每次显示刷新间隔发生的小页面错误数量。[@lst:DumpTopWithMinorFaults](#DumpTopWithMinorFaults) 显示了在编译大型 C++ 项目时使用 `top` 命令查看排名前 10 的进程的转储。附加的 `vMn` 列显示了过去 3 秒内发生的小页面错误数量。

代码清单:编译大型c++项目时，带有附加vMn字段的Linux top命令的转储。 <div id="DumpTopWithMinorFaults"></div>

```shell
   PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND  vMn
341763 dendiba+  20   0  303332 165396  83200 R  99.3   1.0   0:05.09 c++      13k
341705 dendiba+  20   0  285768 153872  87808 R  99.0   1.0   0:07.18 c++       5k
341719 dendiba+  20   0  313476 176236  83328 R  94.7   1.1   0:06.49 c++       8k
341709 dendiba+  20   0  301088 162800  82944 R  93.4   1.0   0:06.46 c++       2k
341779 dendiba+  20   0  286468 152376  87424 R  92.4   1.0   0:03.08 c++      26k
341769 dendiba+  20   0  293260 155068  83072 R  91.7   1.0   0:03.90 c++      22k
341749 dendiba+  20   0  360664 214328  75904 R  88.1   1.3   0:05.14 c++      18k
341765 dendiba+  20   0  351036 205268  76288 R  87.1   1.3   0:04.75 c++      18k
341771 dendiba+  20   0  341148 194668  75776 R  86.4   1.2   0:03.43 c++      20k
341776 dendiba+  20   0  286496 147460  82432 R  76.2   0.9   0:02.64 c++      25k
```

另一种检测运行时小页面错误的方法是使用 `perf stat -e page-faults` 附加到正在运行的进程。

在 HFT 世界中，任何超过 `0` 的页错误都是一个问题。但是对于其他业务领域的低延迟应用程序来说，每秒钟出现 100-1000 次错误的持续情况应该进一步调查。调查运行时小页面错误的根本原因可以像启动 `perf record -e page-faults` 然后 `perf report` 一样简单，以定位有问题的源代码行。

为了在运行时避免页面错误惩罚，您应该在启动时预先为应用程序分配所有内存。一个示例代码可能看起来像这样：

```c++
char *mem = malloc(size);
int pageSize = sysconf(_SC_PAGESIZE)
for (int i = 0; i < size; i += pageSize)
 mem[i] = 0;
```

首先，这段示例代码像往常一样在堆上分配了 `size` 大小的内存。然而，紧接在分配之后，它会逐个页面访问新分配的内存，确保每个页面都加载到 RAM 中。这种方法有助于避免未来访问时因小页面错误造成的运行时延迟。

请看 [@lst:LockPagesAndNoRelease](#LockPagesAndNoRelease) 中更全面的方法，它结合了 `mlock/mlockall` 系统调用对 glibc 分配器进行调整（摘自“实时 Linux Wiki” [^1])。

代码清单:调整glibc分配器以锁定内存中的页，并防止将它们释放到操作系统。 <div id="LockPagesAndNoRelease"></div>

```cpp
#include <malloc.h>
#include <sys/mman.h>

mallopt(M_MMAP_MAX, 0);
mallopt(M_TRIM_THRESHOLD, -1);
mallopt(M_ARENA_MAX, 1);

mlockall(MCL_CURRENT | MCL_FUTURE);

char *mem = malloc(size);
for (int i = 0; i < size; i += sysconf(_SC_PAGESIZE))
    mem[i] = 0;
//...
free(mem);
```

代码 [@lst:LockPagesAndNoRelease](#LockPagesAndNoRelease) 调整了三个 glibc malloc 设置：`M_MMAP_MAX`、`M_TRIM_THRESHOLD` 和 `M_ARENA_MAX`。

- 将 `M_MMAP_MAX` 设置为 `0` 会禁用底层 `mmap` 系统调用用于大分配 - 这是必要的，因为当库尝试将 `mmap` 过的段释放回操作系统时，`mlockall` 可能会被 `munmap` 撤销，从而挫败我们的努力。
- 将 `M_TRIM_THRESHOLD` 设置为 `-1` 可以防止 glibc 在调用 `free` 后将内存返回给操作系统。正如之前所说，此选项对 `mmap` 过的段没有影响。
- 最后，将 `M_ARENA_MAX` 设置为 `1` 可以防止 glibc 通过 `mmap` 分配多个 arena 以容纳多个内核。请记住，后者会妨碍 glibc 分配器多线程可扩展性特性。

结合起来，这些设置将 glibc 强制转换为堆分配，直到应用程序结束才会将内存释放回操作系统。因此，在上述代码中最后一次调用 `free(mem)` 之后，堆将保持相同的尺寸。如果在初始化时分配了足够的空间，任何后续运行时调用 `malloc` 或 `new` 都只会重用预先分配/预处理过的堆区域中的空间。

更重要的是，由于之前的 `mlockall` 调用，之前在 `for` 循环中预处理过的所有堆内存都将保留在 RAM 中 - `MCL_CURRENT` 选项锁定所有当前映射的页面，而 `MCL_FUTURE` 则锁定所有将来会映射的页面。这种使用 `mlockall` 的额外好处是，该进程生成的任何线程的堆栈也将被预处理并锁定。为了更好地控制页面锁定，开发人员应该使用 `mlock` 系统调用，它可以让您选择哪些页面应该保留在 RAM 中。这种技术的缺点是它减少了系统上其他进程可用的内存量。

针对 Windows 的应用程序开发人员应该研究以下 API：使用 `VirtualLock` 锁定页面，使用 `VirtualFree` 和 `MEM_DECOMMIT` 避免立即释放内存，但不使用 `MEM_RELEASE` 标志。

这只是防止运行时小错误的两种示例方法。这些技术中的一些或全部可能已经集成到 jemalloc、tcmalloc 或 mimalloc 等内存分配库中。请查看您选择的库的文档，了解可用的功能。

### 高速缓存预热 {#sec:CacheWarm}

在某些应用程序中，延迟最敏感的部分代码是最不经常执行的。例如，高频交易应用程序会持续从证券交易所读取市场数据信号，一旦检测到有利信号，就会向交易所发送买入订单。在上例工作负载中，读取市场数据的代码路径是最常执行的，而执行买入订单的代码路径很少执行。

由于市场上的其他参与者也可能捕捉到相同的市场信号，策略的成功在很大程度上取决于我们的反应速度，换句话说，取决于我们发送订单到交易所的速度。当我们希望我们的买入订单尽快到达交易所并利用市场数据中检测到的有利信号时，我们最不想遇到的是在决定起飞的那一刻遇到障碍。

当一段代码路径一段时间没有运行时，它的指令和相关数据很可能从 I-cache 和 D-cache 中被驱逐出去。然后，就在我们需要运行这段关键的很少执行的代码时，我们遇到了 I-cache 和 D-cache 未命中惩罚，这可能会让我们输掉比赛。这就是*缓存预热*技术可以发挥作用的地方。

缓存预热涉及定期执行延迟敏感的代码以将其保留在缓存中，同时确保它不会执行任何不需要的操作。执行延迟敏感的代码也会通过将延迟敏感的数据带入其中来“预热”D-cache。这种技术通常用于高频交易应用程序。虽然我们不会提供示例实现，但您可以在 CppCon 2018 lightning talk: [https://www.youtube.com/watch?v=XzRxikGgaHI](https://www.youtube.com/watch?v=XzRxikGgaHI)[^4] 中体验一下。

### 避免 TLB 驱逐

我们从前面章节了解到，TLB 是每个内核的一个快速但有限的虚拟到物理内存地址转换缓存，它减少了耗时的内核页表遍历的需要。当一个进程从一个内核被调度出去，为一个具有完全不同的虚拟地址空间的新进程让路时，属于该内核的 TLB 需要被刷新。除了批发性的 TLB 刷新之外，还有一个更具选择性的过程来使无效的 TLB 条目称为 *TLB 驱逐*。

与基于 MESI 的协议和每个内核的 CPU 缓存（即 L1、L2 和 LLC）不同，硬件本身无法维护核心到核心之间的 TLB 一致性。因此，这项任务必须由内核通过软件来完成。内核通过一种特定的处理器间中断 (IPI) 来实现这个角色，叫做 TLB 驱逐，在 x86 平台上通过 `INVLPG` 汇编指令实现。

TLB 驱逐是实现多线程应用程序低延迟时最容易忽视的陷阱之一。为什么？因为在多线程应用程序中，进程线程共享虚拟地址空间。因此，内核必须在参与线程运行的内核的 TLB 之间通信特定类型的对该共享地址空间的更新。例如，常用的系统调用，如 `munmap`（可以禁用 glibc 分配器使用，参见 [@sec:AvoidPageFaults]）、`mprotect` 和 `madvise`，会影响内核必须在进程的组成线程之间通信的地址空间更改类型。

尽管开发人员可能避免在他的代码中显式使用这些系统调用，但 TLB 驱逐仍然可能来自外部源 - 例如，分配器共享库或操作系统设施。这种类型的 IPI 不仅会扰乱运行时应用程序性能，而且其影响的程度会随着所涉及线程数量的增加而增大，因为中断是在软件中传递的。

如何检测多线程应用程序中的 TLB 驱逐？一种简单的方法是检查 `/proc/interrupts` 中的 TLB 行。一种检测运行时连续 TLB 中断的有用方法是在查看此文件时使用 `watch` 命令。例如，您可以运行 `watch -n5 -d 'grep TLB /proc/interrupts'`, 其中 `-n 5` 选项每 5 秒刷新视图，而 `-d` 则突出显示每次刷新输出之间的差异。

[@lst:ProcInterrupts](#ProcInterrupts) 显示了在运行延迟关键线程的 `CPU2` 处理器上出现大量 TLB 驱逐的 `/proc/interrupts` 转储。注意其他内核数量级上的差异。在这种情况下，这种行为的罪魁祸首是 Linux 内核的一个名为自动 NUMA 平衡的功能，可以通过 `sysctl -w numa_balancing=0` 轻松禁用。

代码清单:一个/proc/interrupts的转储文件，其中显示了CPU2上大量TLB被击落的情况 <div id="ProcInterrupts"></div>

```bash
           CPU0       CPU1       CPU2       CPU3       
...
NMI:          0          0          0          0   Non-maskable interrupts
LOC:     552219    1010298    2272333    3179890   Local timer interrupts
SPU:          0          0          0          0   Spurious interrupts
...
IWI:          0          0          0          0   IRQ work interrupts
RTR:          7          0          0          0   APIC ICR read retries
RES:      18708       9550        771        528   Rescheduling interrupts
CAL:        711        934       1312       1261   Function call interrupts
TLB:       4493       6108      73789       5014   TLB shootdowns
```

但这不是导致 TLB 驱逐的唯一来源。其他来源还包括透明大页、内存压缩、页面迁移和页面缓存回写。垃圾回收器也可以启动 TLB 驱逐。这些特性在履行其职责的过程中会重新定位页面和/或更改页面权限，这需要更新页表，从而导致 TLB 驱逐。

防止 TLB 驱逐需要限制对共享进程地址空间进行的更新次数。在源代码层面，您应该避免运行时执行上述系统调用列表，即 `munmap`、`mprotect` 和 `madvise`。在操作系统层面，禁用内核功能，这些功能会因其功能而导致 TLB 驱逐，例如透明大页和自动 NUMA 平衡。有关 TLB 驱逐的更多细致讨论，以及它们的检测和预防，请阅读 JabPerf 博客上的文章: [https://www.jabperf.com/how-to-deter-or-disarm-tlb-shootdowns/](https://www.jabperf.com/how-to-deter-or-disarm-tlb-shootdowns/)[^5]。

### 防止意外内核节流

C/C++ 编译器是工程领域的杰出成就。然而，它们有时会生成令人惊讶的结果，可能让你陷入无谓的追查中。一个现实例子是编译器优化器发出了你从未打算过的繁重的 AVX 指令。虽然在更现代的芯片上这个问题小了很多，但许多较老的 CPU（仍在本地和云端积极使用）在执行繁重的 AVX 指令时会出现严重的内核节流/降频现象。如果你的编译器在没有你的明确知情或同意的情况下产生了这些指令，你可能会在应用程序运行期间遇到无法解释的延迟异常。

针对这种情况，如果您不希望使用繁重的 AVX 指令，可以将 "-mprefer-vector-width=###" 添加到您的编译标志中，将最高宽度指令集固定为 128 或 256。同样，如果您整个服务器集群运行的是最新芯片，那么也不用太担心，因为 AVX 指令集的节流影响现在已经微乎其微。

[^1]: Linux 基金会 Wiki：实时应用程序内存 - [https://wiki.linuxfoundation.org/realtime/documentation/howto/applications/memory](https://wiki.linuxfoundation.org/realtime/documentation/howto/applications/memory)
[^4]: 缓存预热技术 - [https://www.youtube.com/watch?v=XzRxikGgaHI](https://www.youtube.com/watch?v=XzRxikGgaHI)
[^5]: JabPerf 博客：TLB 驱逐 - [https://www.jabperf.com/how-to-deter-or-disarm-tlb-shootdowns/](https://www.jabperf.com/how-to-deter-or-disarm-tlb-shootdowns/)

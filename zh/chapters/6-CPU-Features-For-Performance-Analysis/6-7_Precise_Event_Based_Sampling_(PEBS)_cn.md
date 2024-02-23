## 基于硬件的采样功能

主要 CPU 供应商提供了一系列附加功能来增强性能分析。由于 CPU 供应商以不同的方式处理性能监控，因此这些功能不仅在调用方式上存在差异，而且在功能上也存在差异。在 Intel 处理器中，它被称为处理器事件采样 (PEBS)，首次引入于 NetBurst 微架构。AMD 处理器上类似的功能称为指令采样 (IBS)，从 AMD Opteron 家族 (10h 代) 核心开始可用。接下来，我们将更详细地讨论这些功能，包括它们的相似之处和不同之处。

### 英特尔平台上的 PEBS

与最后分支记录类似，PEBS 用于在分析程序时捕获每个收集到的样本的额外数据。当性能计数器配置为 PEBS 时，处理器会保存一组具有定义格式的额外数据，称为 PEBS 记录。英特尔 Skylake CPU 的 PEBS 记录格式如图 @fig:PEBS_record 所示。记录包含通用寄存器状态 (`EAX`, `EBX`, `ESP` 等）、`EventingIP`, `Data Linear Address` 和稍后将讨论的 `延迟值`。PEBS 记录的内容布局因不同的微架构而异，请参阅 [@IntelOptimizationManual, 第 3B 卷，第 20 章 性能监控]。

![PEBS记录格式适用于第六代、第七代和第八代英特尔酷睿处理器家族。 *© Image from [@IntelOptimizationManual, Volume 3B, Chapter 20].*](../../img/pmu-features/PEBS_record.png){#fig:PEBS_record width=90%}

从 Skylake 架构开始，PEBS 记录已经增强，可以收集 XMM 寄存器和 LBR 记录。格式已经重新组织，将字段分组为基本组、内存组、GPR 组、XMM 组和 LBR 组。性能分析工具可以选择感兴趣的数据组，从而减小记录大小并降低记录生成延迟。默认情况下，PEBS 记录只包含基本组。

使用 PEBS 的一个显著优点是与基于中断的常规采样相比，采样开销更低。回想一下，当计数器溢出时，CPU 会生成中断来收集一个样本。频繁地生成中断并让分析工具本身在中断服务例程中捕获程序状态是非常昂贵的，因为它涉及操作系统交互。

另一方面，PEBS 维护了一个缓冲区，用于临时存储多个 PEBS 记录。假设我们使用 PEBS 对加载事件进行采样。当性能计数器配置为 PEBS 时，计数器溢出条件不会触发中断，而是会激活 PEBS 机制。该机制将捕获下一个加载，捕获一个新的记录并将其存储在专用的 PEBS 缓冲区区域。该机制还会清除计数器溢出状态并重新加载计数器以初始值。只有当专用缓冲区已满时，处理器才会引发中断，缓冲区才会刷新到内存。这种机制通过减少中断触发次数来降低采样开销。

Linux 用户可以通过执行 `dmesg` 检查 PEBS 是否已启用：

```bash
$ dmesg | grep PEBS
[    0.113779] Performance Events: XSAVE Architectural LBR, PEBS fmt4+-baseline,  
AnyThread deprecated, Alderlake Hybrid events, 32-deep LBR, full-width counters, Intel PMU driver.
```

对于 LBR，Linux perf 会在每个收集到的样本中转储整个 LBR 堆栈内容。因此，可以分析由 Linux perf 收集的原始 LBR 转储。但是，对于 PEBS，Linux `perf` 不会像 LBR 那样导出原始输出。相反，它会处理 PEBS 记录并仅提取根据特定需求的数据子集。因此，无法使用 Linux `perf` 访问原始 PEBS 记录的集合。但是，Linux `perf` 提供了一些从原始样本处理过的 PEBS 数据，可以通过 `perf report -D` 访问。要转储原始 PEBS 记录，可以使用 `pebs-grabber`: [https://github.com/andikleen/pmu-tools/tree/master/pebs-grabber](https://github.com/andikleen/pmu-tools/tree/master/pebs-grabber)[^1] 工具。

### AMD 平台上的 IBS

指令采样 (IBS) 是 AMD64 处理器的一项功能，可用于收集与指令提取和指令执行相关的特定指标。AMD 处理器的处理器流水线由两个独立的阶段组成：一个前端阶段负责提取 AMD64 指令字节，一个后端阶段负责执行“ops”。由于这些阶段在逻辑上是分开的，因此存在两个独立的采样机制：IBS Fetch 和 IBS Execute。

- IBS Fetch 监控流水线的前端，并提供有关 ITLB (命中或未命中)、I-cache (命中或未命中)、获取地址、获取延迟等信息。
- IBS Execute 监控流水线的后端，通过跟踪单个 op 的执行来提供关于指令执行行为的信息。例如：分支 (是否被执行，是否被预测)、加载/存储 (D-cache 和 DTLB 中的命中或未命中，线性地址，加载延迟)。

PMC 和 IBS 在 AMD 处理器之间存在一些重要差异。PMC 计数器是可编程的，而 IBS 则类似于固定计数器。IBS 计数器只能用于监控启用或禁用，无法针对任何选择性事件进行编程。IBS Fetch 和 Execute 计数器可以独立启用/禁用。使用 PMC 时，用户必须提前决定要监控哪些事件。使用 IBS 时，会为每个采样的指令收集丰富的数据，然后由用户分析他们感兴趣的数据部分。IBS 选择并标记要监控的指令，然后捕获该指令执行期间引起的微架构事件。有关 Intel PEBS 和 AMD IBS 的更多详细比较，请参见 [@ComparisonPEBSIBS]。

由于 IBS 被集成到处理器流水线中并作为固定事件计数器，因此样本收集开销最小。分析器需要处理 IBS 生成的数据，这些数据可能非常庞大，具体取决于采样间隔、配置的线程数、是否配置 Fetch/Execute 等。在 Linux 内核版本 6.1 之前，IBS 总是为所有内核收集样本。这个限制会导致巨大的数据收集和处理开销。从内核 6.2 开始，Linux perf 只支持为配置的内核收集 IBS 样本。

IBS 由 Linux perf 和 AMD uProf 分析器支持。以下是收集 IBS 执行和获取样本的示例命令：

```bash
$ perf record -a -e ibs_op/cnt_ctl=1,l3missonly=0/ -- benchmark.exe
$ perf record -a -e ibs_fetch/l3missonly=1/ -- benchmark.exe
$ perf report
```
在上一个命令中，`cnt_ctl=0` 表示计数时钟周期，`cnt_ctl=1` 表示在间隔期间计数已分配的 ops；`l3missonly=1` 只保留具有 L3 未命中的样本。请注意，在上述两个命令中，都使用了 `-a` 选项来为所有内核收集 IBS 样本，否则 `perf` 在 Linux 内核 6.1 上无法收集样本。从 6.2 版本开始，除非您想要为所有内核收集 IBS 样本，否则不再需要 `-a` 选项。`perf report` 命令将显示类似于常规 PMU 事件的与函数和源代码行关联的样本，但会提供我们稍后讨论的附加功能。

[TODO]: 这些 `cnt_ctl,l3missonly` IBS 控件/过滤器是否是唯一存在的？它们在哪里记录？
[TODO]: 如果我想进行自定义分析，如何解析 IBS 原始转储？

### ARM 平台上的 SPE

Arm Statistical Profiling Extension (SPE) 是一项架构功能，旨在增强 Arm CPU 内的指令执行性能分析。自 2019 年推出的 Neoverse N1 核心以来，这项功能就可用。SPE 功能扩展被指定为 Armv8-A 架构的一部分，从 Arm v8.2 起提供支持。与其他解决方案相比，SPE 更类似于 AMD IBS，而不是 Intel PEBS。类似于 IBS，SPE 与通用性能监测器计数器 (PMC) 分开，但它只有一个机制，而不是两种类型的 IBS（获取和执行）。

[TODO]: SPE 是否可选？例如，它是否可用于 Apple/Qualcomm 硅？

SPE 采样过程内置于指令执行流水线中。样本收集仍然基于可配置的间隔，但操作是根据统计信息选择的。每个采样的操作都会生成一个样本记录，其中包含有关此操作执行的各种数据。SPE 记录保存指令地址，负载和存储访问的数据的虚拟和物理地址，数据访问的来源（缓存或 DRAM）以及时间戳，以与系统中其他事件进行关联。此外，它还可以提供各种流水线阶段的延迟，例如发出延迟（从调度到执行）、转换延迟（虚拟到物理地址转换的周期数）和执行延迟（功能单元中负载/存储的延迟）。白皮书 [@ARMSPE] 更详细地描述了 ARM SPE，并展示了一些使用它的优化示例。

类似于 Intel PEBS 和 AMD IBS，ARM SPE 有助于减少采样开销并支持更长的收集。除此之外，它还支持样本记录的后过滤，这有助于减少存储所需内存。

SPE 分析已在 Linux `perf` 工具中启用，可以使用以下方式：

```bash
$ perf record -e arm_spe_0/<controls>/ -- test_program
$ perf report --stdio
$ spe-parser perf.data -t csv
```

其中 `<controls>` 允许您可选地指定收集的各种控件和过滤器。 `perf report` 将根据用户使用 `<controls>` 选项所要求的内容提供通常的输出。 `spe-parser`[^5] 是由 ARM 工程师开发的工具，用于解析捕获的 perf 记录数据并将所有 SPE 记录保存到 CSV 文件中。

[TODO]: 是否可以在 Windows 上 ARM 上使用 SPE？`WindowsPerf` 是否可以收集可由 `spe-parser` 解析的 SPE 数据？

### 精确事件

现在我们已经介绍了高级采样功能，让我们讨论一下 **如何** 使用它们来改善性能分析。我们将从精确事件的概念开始。

性能分析的一个主要问题是精确地定位导致特定性能事件的指令。正如 [@sec:profiling] 中所讨论的，基于中断的采样基于计数特定性能事件并等待其溢出。当溢出中断发生时，处理器需要一段时间停止执行并标记导致溢出的指令。对于现代复杂的乱序 CPU 架构来说，这一点尤其困难。

它引入了滑动的概念，滑动定义为导致事件的 IP (指令地址) 与事件被标记的 IP 之间的距离。滑动使得难以发现导致性能问题的指令。考虑一个具有大量缓存未命中的应用程序，其热门汇编代码如下所示：

```asm
; load1 
; load2
; load3
```

分析器可能会将 `load3` 标记为导致大量缓存未命中的指令，而实际上，真正的罪魁祸首是 `load1`。对于高性能处理器，这种滑动可能数百条处理器指令。这通常会让性能工程师感到非常困惑。有兴趣的读者可以访问 Intel 开发者专区网站: [https://software.intel.com/en-us/vtune-help-hardware-event-skid](https://software.intel.com/en-us/vtune-help-hardware-event-skid)[^4] 了解更多关于此类问题基础原因的信息。

通过让处理器本身存储指令指针（以及其他信息）可以缓解滑移问题。使用 Intel PEBS 时，PEBS 记录中的 `EventingIP` 字段指示导致事件的指令。这通常仅适用于受支持事件的一个子集，称为“精确事件”。可以在 [@IntelOptimizationManual, 第 3B 卷，第 20 章 性能监控] 中找到特定微架构的精确事件完整列表。有关使用 PEBS 精确事件缓解滑移的示例，请参见 easyperf 博客: [https://easyperf.net/blog/2018/08/29/Understanding-performance-events-skid](https://easyperf.net/blog/2018/08/29/Understanding-performance-events-skid).[^2]

以下是 Skylake 微架构的精确事件列表：

```
INST_RETIRED.*          OTHER_ASSISTS.*      BR_INST_RETIRED.*       BR_MISP_RETIRED.*
FRONTEND_RETIRED.*      HLE_RETIRED.*        RTM_RETIRED.*           MEM_INST_RETIRED.*
MEM_LOAD_RETIRED.*      MEM_LOAD_L3_HIT_RETIRED.*
```
其中 ``*`` 表示组内所有子事件都可以配置为精确事件。

使用 Intel 平台上 Linux `perf` 的用户应在上述列出的事件之一中添加 `pp` 后缀以启用精确标记：

```bash
$ perf record -e cycles:pp -- ./a.exe
```

[TODO]: Denis 展示常规事件和精确事件的示例？

对于 AMD IBS 和 ARM SPE，所有收集的样本在设计上都是精确的，因为硬件会捕获确切的指令地址。事实上，它们都以非常相似的方式工作。每当溢出发生时，该机制将导致溢出的指令保存到专用缓冲区中，然后由中断处理程序读取。由于地址被保留，因此 IBS 和 SPE 样本与指令的关联是精确的。

[TODO]: Linux perf 在 ARM 上支持 `:p` 后缀吗？

精确事件为性能工程师提供了便利，因为它们有助于避免误导性数据，这些数据经常让初学者甚至高级开发人员感到困惑。TMA 方法论依赖精确事件来定位低效执行发生的源代码确切行。

## 分析内存访问 {#sec:sec_PEBS_DLA}

内存访问是许多应用程序性能的关键因素。PEBS 和 IBS 都能够收集程序中内存访问的详细信息。例如，您不仅可以对加载进行采样，还可以收集它们的目标地址和访问延迟。请记住，这并不跟踪所有存储和加载。否则，开销会太大。相反，它只分析大约每 10 万次访问中的一个访问。您可以自定义每秒需要多少个样本。通过足够的样本收集，可以提供内存访问的准确统计图片。

在 PEBS 中，允许实现此功能的功能称为数据地址分析 (DLA)。为了提供有关采样加载和存储的更多信息，它使用 PEBS 设施内的“Data Linear Address”和“Latency Value”字段（参见图 @fig:PEBS_record）。如果性能事件支持 DLA 功能并且 DLA 已启用，处理器将转储所采样内存访问的内存地址和延迟。您还可以过滤延迟高于某个阈值的内存访问。这对于查找可能成为许多应用程序性能瓶颈的长延迟内存访问非常有用。

使用 IBS Execute 和 ARM SPE 采样，您还可以深入分析应用程序执行的内存访问。一种方法是转储收集的样本并手动处理它们。IBS 会保存确切的线性地址、其延迟、访问来自何处（缓存或 DRAM）、以及它是否在 DTLB 中命中或未命中。SPE 可用于估计内存子系统组件的延迟和带宽、估计单个加载/存储的内存延迟等等。

这些扩展最重要的用例之一是检测真实共享和虚假共享，我们将在 [@sec:TrueFalseSharing] 中讨论。Linux `perf c2c` 工具大量依赖所有三种机制（PEBS、IBS 和 SPE）来查找可能遇到真实/虚假共享的争用内存访问：它匹配不同线程的加载/存储地址，并检查命中是否发生在由其他线程修改的缓存行中。

[^1]: PEBS 抓取器工具 - [https://github.com/andikleen/pmu-tools/tree/master/pebs-grabber](https://github.com/andikleen/pmu-tools/tree/master/pebs-grabber)。需要 root 权限。
[^2]: 性能滑移 - [https://easyperf.net/blog/2018/08/29/Understanding-performance-events-skid](https://easyperf.net/blog/2018/08/29/Understanding-performance-events-skid)
[^4]: 硬件事件滑移 - [https://software.intel.com/en-us/vtune-help-hardware-event-skid](https://software.intel.com/en-us/vtune-help-hardware-event-skid)
[^5]: ARM SPE 解析器 - [https://gitlab.arm.com/telemetry-solution/telemetry-solution](https://gitlab.arm.com/telemetry-solution/telemetry-solution)

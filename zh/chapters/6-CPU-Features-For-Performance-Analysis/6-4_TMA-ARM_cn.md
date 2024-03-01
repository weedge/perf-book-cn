### TMA 在 ARM 处理器上

ARM CPU 架构师也为他们的处理器开发了一种 TMA 性能分析方法，我们接下来将讨论。ARM 在其文档中将其称为“Topdown” [[@ARMNeoverseV1](../References.md#ARMNeoverseV1)TopDown]，因此我们将使用他们的命名。在撰写本章节时（2023 年底），Topdown 仅支持 ARM 设计的内核，例如 Neoverse N1 和 Neoverse V1 及其衍生产品，例如 Ampere Altra 和 AWS Graviton3。如果您需要刷新有关 ARM 芯片系列的记忆，请参考本书末尾的主要 CPU 微架构列表。Apple 设计的处理器目前还不支持 ARM Topdown 性能分析方法。

Neoverse V1 是 Neoverse 系列中第一个支持全套 1 级 Topdown 指标的 CPU：`Bad Speculation`、`Frontend Bound`、`Backend Bound` 和 `Retiring`。据说未来的 Neoverse 内核将支持更高级别的 TMA。在撰写本文时，没有针对 Neoverse N2 和 V2 内核的分析指南。在 V1 内核之前，Neoverse N1 只支持两个 L1 类别：`Frontend Stalled Cycles` 和 `Backend Stalled Cycles`。

为了演示基于 V1 处理器的 ARM Topdown 分析，我们启动了一个由 AWS Graviton3 驱动的 AWS EC2 `m7g.metal` 实例。请注意，由于虚拟化，Topdown 可能无法在其他非金属实例类型上运行。我们请求了由 AWS 管理的 64 位 ARM `Ubuntu 22.04 LTS` 以及 `Linux kernel 6.2`。提供的 `m7g.metal` 实例有 64 个 vCPU 和 256 GB 的内存。

我们将 Topdown 方法应用于 AI Benchmark Alpha: [https://ai-benchmark.com/alpha.html](https://ai-benchmark.com/alpha.html)，[^1] 它是一个用于评估各种硬件平台（包括 CPU、GPU 和 TPU）的 AI 性能的开源 Python 库。该基准测试依赖 TensorFlow 机器学习库来测量关键深度学习模型的推理和训练速度。AI Benchmark Alpha 总共包含 42 个测试，包括分类、图像分割、文本翻译等等。

ARM 工程师开发了 topdown-tool: [https://learn.arm.com/install-guides/topdown-tool/](https://learn.arm.com/install-guides/topdown-tool/)[^2]，我们将在下面使用它。该工具可以在 Linux 和 Windows 上的 ARM 上运行。在 Linux 上，它使用标准的 perf 工具，而在 Windows 上，它使用 WindowsPerf: [https://gitlab.com/Linaro/WindowsPerf/windowsperf](https://gitlab.com/Linaro/WindowsPerf/windowsperf)[^3]，这是一款 Windows on Arm 性能分析工具。类似于 Intel 的 TMA，ARM 的方法也采用了“向下钻取”的概念，即首先确定高级性能瓶颈，然后向下钻取更细致的根本原因分析。以下是我们使用的命令：

```bash
$ topdown-tool --all-cpus -m Topdown_L1 -- python -c "from ai_benchmark import AIBenchmark; results = AIBenchmark(use_CPU=True).run()"
Stage 1 (Topdown metrics)
=========================
[Topdown Level 1]
Frontend Bound... 16.48% slots
Backend Bound.... 54.92% slots
Retiring......... 27.99% slots
Bad Speculation..  0.59% slots
```

其中 `--all-cpus` 选项启用所有 CPU 的系统级收集，而 `-m Topdown_L1` 则收集 Topdown 1 级指标。 `--` 后面的所有内容都是运行 AI Benchmark Alpha 套件的命令行。

从上面的输出中，我们可以得出结论，基准测试不会出现分支预测错误。此外，如果不深入了解所涉及的工作负载，就很难说 16.5% 的“前端瓶颈”是否值得关注，因此我们将注意力转移到“后端瓶颈”指标上，该指标显然是停滞周期的主要来源。基于 Neoverse V1 的芯片没有二级细分，相反，该方法建议通过收集一组相应的指标来进一步探索有问题的类别。以下是我们如何深入研究更详细的“后端瓶颈”分析：

```bash
$ topdown-tool --all-cpus -n BackendBound -- python -c "from ai_benchmark import AIBenchmark; results = AIBenchmark(use_CPU=True).run()"
Stage 1 (Topdown metrics)
=========================
[Topdown Level 1]
Backend Bound......................... 54.70% slots

Stage 2 (uarch metrics)
=======================
  [Data TLB Effectiveness]
  DTLB MPKI........................... 0.413 misses per 1,000 instructions
  L1 Data TLB MPKI.................... 3.779 misses per 1,000 instructions
  L2 Unified TLB MPKI................. 0.407 misses per 1,000 instructions
  DTLB Walk Ratio..................... 0.001 per TLB access
  L1 Data TLB Miss Ratio.............. 0.013 per TLB access
  L2 Unified TLB Miss Ratio........... 0.112 per TLB access

  [L1 Data Cache Effectiveness]
  L1D Cache MPKI...................... 13.114 misses per 1,000 instructions
  L1D Cache Miss Ratio................  0.046 per cache access

  [L2 Unified Cache Effectiveness]
  L2 Cache MPKI....................... 1.458 misses per 1,000 instructions
  L2 Cache Miss Ratio................. 0.027 per cache access

  [Last Level Cache Effectiveness]
  LL Cache Read MPKI.................. 2.505 misses per 1,000 instructions
  LL Cache Read Miss Ratio............ 0.219 per cache access
  LL Cache Read Hit Ratio............. 0.783 per cache access

  [Speculative Operation Mix]
  Load Operations Percentage.......... 25.36% operations
  Store Operations Percentage.........  2.54% operations
  Integer Operations Percentage....... 29.60% operations
  Advanced SIMD Operations Percentage. 10.93% operations
  Floating Point Operations Percentage  6.85% operations
  Branch Operations Percentage........ 10.04% operations
  Crypto Operations Percentage........  0.00% operations
```

Misc 类别包含不在主类别中的指令。例如，barriers

在上面的命令中，选项 `-n BackendBound` 收集与 `Backend Bound` 类别及其后代相关的所有指标。输出中每个指标的描述在 [[@ARMNeoverseV1](../References.md#ARMNeoverseV1)TopDown] 中给出。请注意，它们与我们在 [@sec:PerfMetricsCaseStudy] 中讨论的非常相似，因此您可能也想重新查看它。

我们的目标不是优化基准测试，而是要描述性能瓶颈。但是，如果有这样的任务，我们的分析可以继续进行。有大量的 `L1 Data TLB` 未命中（3.8 MPKI），但随后 90% 的未命中命中 L2 TLB（参见 `L2 Unified TLB Miss Ratio`）。总而言之，只有 0.1% 的 TLB 未命中导致页表遍历（参见 `DTLB Walk Ratio`），这表明这不是我们的主要关注点，尽管快速使用大页面的实验仍然值得。

查看 `L1/L2/LL Cache Effectiveness` 指标，我们可以发现数据缓存未命中的潜在问题。对 L1D 缓存的 ~22 次访问中就有一次会导致未命中（参见 `L1D Cache Miss Ratio`），这是可以容忍但仍然很昂贵的。对于 L2，这个数字是 37 分之一（参见 `L2 Cache Miss Ratio`），这要好得多。然而对于 LLC，`LL Cache Read Miss Ratio` 是不令人满意的：每 4 次访问就会导致一次失败。由于这是一个 AI 基准测试，其中大部分时间可能花在矩阵乘法上，因此循环阻塞等代码转换可能会有所帮助（参见 [@sec:LoopOpts])。



最后一类给出了操作组合，这在某些情况下很有用。在我们的例子中，我们应该关注 SIMD 操作的低百分比，特别是考虑到使用了高度优化的 `Tensorflow` 和 `numpy` 库。相比之下，整数运算和分支的百分比似乎太高了。分支可能来自 Python 解释器或过多的函数调用。而高百分比的整数操作可能是由于缺乏向量化或线程同步造成的。 [[@ARMNeoverseV1](../References.md#ARMNeoverseV1)TopDown] 给出了一个使用来自 `Speculative Operation Mix` 类别的数据发现向量化机会的示例。

在我们的案例研究中，我们运行了两次基准测试，但在实践中，一次运行通常就足够了。运行没有选项的 `topdown-tool` 将使用单次运行收集所有可用的指标。此外，`-s combined` 选项将按 L1 类别对指标进行分组，并以类似于 `Intel Vtune`、`toplev` 和其他工具的格式输出数据。进行多次运行的唯一实际原因是工作负载具有突发行为，其非常短的阶段具有不同的性能特征。在这种情况下，您希望避免事件多路复用（参见 [@sec:secMultiplex]）并通过多次运行工作负载来提高收集准确性。

AI Benchmark Alpha 有各种可能表现出不同性能特征的测试。上面显示的输出汇总了所有基准并给出了总体细分。如果单个测试确实存在不同的性能瓶颈，这通常不是一个好主意。您需要对每个测试进行单独的 Topdown 分析。 `topdown-tool` 可以提供帮助的一种方法是使用 `-i` 选项，该选项将根据可配置的时间间隔输出数据。然后，您可以比较间隔并决定下一步。


[^1]: AI Benchmark Alpha - [https://ai-benchmark.com/alpha.html](https://ai-benchmark.com/alpha.html)
[^2]: ARM `topdown-tool` - [https://learn.arm.com/install-guides/topdown-tool/](https://learn.arm.com/install-guides/topdown-tool/)
[^3]: WindowsPerf - [https://gitlab.com/Linaro/WindowsPerf/windowsperf](https://gitlab.com/Linaro/WindowsPerf/windowsperf)
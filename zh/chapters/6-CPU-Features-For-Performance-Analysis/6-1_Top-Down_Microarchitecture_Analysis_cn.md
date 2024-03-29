
## 自顶向下微架构分析 (TMA) {#sec:TMA}

自顶向下微架构分析 (TMA) 方法是一种非常强大的技术，用于识别程序中的 CPU 瓶颈。它是一种健壮、正式的方法，即使是经验不足的开发人员也易于使用。该方法最棒的一点是，它不需要开发人员深入了解系统中的微架构和 PMCs，即可高效找到 CPU 瓶颈。

从概念层面来看，TMA 识别导致程序执行停滞的原因。图 [@fig:TMA_concept](#TMA_concept) 展示了 TMA 的核心思想。这不是实际分析的运作方式，因为分析每个微操作 (μop) 会非常慢。尽管如此，该图有助于理解该方法。

![TMA 顶级细分的概念。(*© 图像来自 [[@TMA_ISPASS](../References.md#TMA_ISPASS)]*)](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/pmu-features/TMAM_diag.png)<div id="TMA_concept"></div>

下面是如何阅读此图的简短指南。正如我们从 [@sec:uarch] 中所知，CPU 内部有缓冲区来跟踪正在执行的 μop 的信息。每当获取和解码新指令时，都会在这些缓冲区中分配新条目。如果指令的 μop 在特定执行周期内未分配，可能是两个原因之一：我们无法获取和解码它（“前端受限”）；或者后端工作超载，无法为新的 μop 分配资源（“后端受限”）。如果 μop 已分配并安排执行但从未退休，则意味着它来自预测错误的路径（“错误猜测”）。最后，“退休”代表正常执行。它是我们希望所有 μop 都处的桶，尽管有一些例外情况，我们稍后会讨论。

为了实现其目标，TMA 通过监控特定的一组性能事件并根据预定义的公式计算指标来观察程序的执行。基于这些指标，TMA 通过将程序分配到四个高级桶之一来对其进行表征。这四个高级类别中的每一个都具有多个嵌套级别，CPU 供应商可以选择不同的实现方式。每代处理器计算这些指标的公式可能会有所不同，因此最好依赖工具进行分析，而不是自己尝试计算。

在接下来的部分中，我们将讨论 AMD、ARM 和 Intel 处理器中的 TMA 实现。

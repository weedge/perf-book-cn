---
typora-root-url: ..\..\img
---

## 管道槽

另一个一些性能工具使用的重要指标是**管道槽 (pipeline slot)** 的概念。管道槽代表处理一个微操作所需的硬件资源。图 @fig:PipelineSlot 展示了一个每周期有 4 个分配槽的 CPU 的执行管道。这意味着核心可以在每个周期将执行资源（重命名的源和目标寄存器、执行端口、ROB 条目等）分配给 4 个新的微操作。这样的处理器通常被称为**4 宽机器**。在图中连续的六个周期中，只利用了一半可用槽位。从微架构的角度来看，执行此类代码的效率只有 50%。

![4 宽 CPU 的管道图](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/terms-and-metrics/PipelineSlot.jpg){#fig:PipelineSlot width=40% }

英特尔的 Skylake 和 AMD Zen3 内核具有 4 宽分配。英特尔的 SunnyCove 微架构采用 5 宽设计。截至 2023 年，最新的 Goldencove 和 Zen4 架构都采用 6 宽分配。Apple M1 的设计没有官方披露，但测得为 8 宽。[^1]

管道槽是自顶向下微架构分析 (见 [@sec:TMA]) 的核心指标之一。例如，前端受限和后端受限指标由于各种瓶颈而表示为未使用的管道槽的百分比。

[^1]: Apple 微架构研究 - [https://dougallj.github.io/applecpu/firestorm.html](https://dougallj.github.io/applecpu/firestorm.html)

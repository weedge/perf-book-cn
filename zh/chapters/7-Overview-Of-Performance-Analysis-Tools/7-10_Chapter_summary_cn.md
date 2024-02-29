## 章节总结 

* 我们快速概述了三大平台（Linux、Windows 和 MacOS）上最流行的工具。根据 CPU 供应商的不同，性能分析工具的选择也会有所不同。对于使用英特尔处理器的系统，我们推荐使用 Vtune；对于使用 AMD 处理器的系统，我们推荐使用 uProf；对于苹果平台，我们推荐使用 Xcode Instruments。

* Linux perf 可能是在 Linux 上使用最频繁的性能分析工具。它支持所有主要 CPU 供应商的处理器。但是它没有图形界面，不过有一些免费工具可以可视化 perf 的分析数据。

* 我们还讨论了 Windows 事件跟踪 (ETW)，它旨在观察运行系统中的软件动态。Linux 有一个类似的工具叫做 KUtrace: [https://github.com/dicksites/KUtrace](https://github.com/dicksites/KUtrace)，[^1] 我们这里不进行介绍。

* 此外，还有混合性能分析器，它结合了代码植入、采样和跟踪等技术。这结合了这些方法的优点，允许用户获得特定代码段非常详细的信息。本章中，我们介绍了 Tracy，它在游戏开发人员中非常流行。

* 连续性能分析器已经成为监控生产环境性能的重要工具。它们可以收集系统级的性能指标，包括调用堆栈，持续时间可达数天、数周甚至数月。这些工具可以更容易地发现性能变化的点和问题的根源。

[^1]: KUtrace - [https://github.com/dicksites/KUtrace](https://github.com/dicksites/KUtrace)



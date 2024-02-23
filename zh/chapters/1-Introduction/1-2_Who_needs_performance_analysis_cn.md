## 谁需要性能调优？

在像高性能计算（HPC）、云服务、高频交易（HFT）、游戏开发和其他对性能要求极高的领域，性能工程无需多加辩解。例如，谷歌曾报告说，搜索慢2%导致每位用户搜索减少2%。[^3] 对于Yahoo!来说，页面加载速度快了400毫秒导致流量增加了5-9%。[^4] 在这个数字游戏中，微小的改进可能产生显著影响。这些例子证明，服务工作得越慢，使用的人就越少。

有一句著名的话：“过早优化是万恶之源”。但相反的情况也经常成立。推迟性能工程工作可能为时已晚，导致的问题可能和过早优化一样恶劣。对于从事性能关键项目的开发人员来说，了解底层硬件工作原理是至关重要的。在这些行业中，如果一个程序在开发过程中没有以硬件为焦点，那就是注定会失败的。软件的性能特性必须与正确性和安全性一样受到重视，从第一天开始。ClickHouse数据库就是一个成功的软件产品，它是围绕一个小而非常高效的核心构建的。

有趣的是，性能工程不仅在上述领域需要。如今，在通用应用程序和服务领域也需要性能工程。我们每天使用的许多工具，如果不能满足其性能要求，就根本不会存在。例如，集成到Microsoft Visual Studio IDE中的Visual C++ IntelliSense[^2]功能具有非常严格的性能约束。为了使IntelliSense自动完成功能正常工作，它们必须在毫秒级别内解析整个源代码库。[^5] 如果源代码编辑器花费几秒钟才能建议自动完成选项，那么没有人会使用它。这样的功能必须非常响应迅速，并在用户输入新代码时提供有效的继续建议。只有通过注重性能并经过深思熟虑的性能工程，才能取得类似应用程序的成功。

有时，快速的工具会在它们最初设计的领域之外找到用途。例如，如今，游戏引擎如Unreal[^6]和Unity[^7]在建筑、3D可视化、电影制作等领域中也得到了应用。由于游戏引擎非常高效，它们是需要2D和3D渲染、物理引擎、碰撞检测、声音、动画等功能的应用程序的自然选择。

> "快速的工具不仅允许用户更快地完成任务，还允许用户以全新的方式完成完全新的任务。" - Nelson Elhage在他的博客文章中写道（2020年）[^1]。

我希望不用说人们讨厌使用慢软件。应用程序的性能特性可能是用户切换到竞争对手产品的唯一因素。通过强调性能，您可以为您的产品赢得竞争优势。

性能工程是一项重要而有益的工作，但可能非常耗时。事实上，性能优化是一场永无止境的游戏。总会有一些地方需要优化。不可避免地，开发人员会达到边际收益的点，在这一点上，进一步的改进将以非常高的工程成本为代价，并且可能不值得努力。应用程序针对硬件理论极限的性能评估有助于了解优化的潜在空间。知道何时停止优化是性能工作的关键方面。有些组织通过将这些信息集成到代码审查流程中来实现：源代码行用相应的“成本”指标进行注释。使用这些数据，开发人员可以决定是否值得优化代码的特定部分。

在开始性能调优之前，请确保有足够的理由这样做。为了优化而优化是没有价值的，如果它不能为您的产品增加价值。慎重的性能工程始于明确定义的性能目标，说明您试图实现什么以及为什么这样做。此外，您还应该选择用于衡量是否达到目标的指标。您可以在[@SystemsPerformance]和[@Akinshin2019]中阅读有关设置性能目标的更多信息。

尽管如此，实践和掌握性能分析和调优的技能总是很好的。如果您因此原因拿起了这本书，那么非常欢迎您继续阅读。

[^1]: N. Elhage的软件性能反思 - [https://blog.nelhage.com/post/reflections-on-performance/](https://blog.nelhage.com/post/reflections-on-performance/)
[^2]: Visual C++ IntelliSense - [https://docs.microsoft.com/en-us/visualstudio/ide/visual-cpp-intellisense](https://docs.microsoft.com/en-us/visualstudio/ide/visual-cpp-intellisense)
[^3]: Marissa Mayer的演讲幻灯片 - [https://assets.en.oreilly.com/1/event/29/Keynote Presentation 2.pdf](https://assets.en.oreilly.com/1/event/29/Keynote Presentation 2.pdf)
[^4]: Stoyan Stefanov的演讲幻灯片 - [https://www.slideshare.net/stoyan/dont-make-me-wait-or-building-highperformance-web-applications](https://www.slideshare.net/stoyan/dont-make-me-wait-or-building-highperformance-web-applications)
[^5]: 事实上，不可能在毫秒级的时间内解析整个代码库。相反，IntelliSense只重构AST中已更改的部分。请在视频中观看微软团队如何实现这一目标的更多细节:  [https://channel9.msdn.com/Blogs/Seth-Juarez/Anders-Hejlsberg-on-Modern-Compiler-Construction](https://channel9.msdn.com/Blogs/Seth-Juarez/Anders-Hejlsberg-on-Modern-Compiler-Construction).
[^6]: Unreal Engine - [https://www.unrealengine.com](https://www.unrealengine.com).
[^7]: Unity Engine - [https://unity.com/](https://unity.com/)

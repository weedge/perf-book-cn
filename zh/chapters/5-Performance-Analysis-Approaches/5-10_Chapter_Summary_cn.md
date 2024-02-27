## 章节总结 {.unlisted .unnumbered}

* 延迟和吞吐量通常是程序性能的最终指标。当寻求改善它们的方法时，我们需要获取更多关于应用程序如何执行的详细信息。硬件和软件都提供可用于性能监视的数据。

* 代码检测允许我们跟踪程序中的许多内容，但会在开发和运行时都造成相对较大的开销。虽然现在开发人员很少手动检测他们的代码，但这种方法仍然与自动化流程相关，例如 PGO。

* 跟踪在概念上类似于检测，可用于探索系统中的异常。跟踪允许我们捕获整个事件序列，并在每个事件上附加时间戳。

* 工作负载特征化是一种基于应用程序运行时行为进行比较和分组的方法。一旦进行特征化，就可以遵循特定的方法来找到程序中的优化空间。带有标记 API 的分析工具可用于分析特定代码区域的性能。

* 采样跳过程序执行的大部分，只获取一个样本，该样本应该代表整个区间。尽管如此，采样通常会产生足够精确的分布。采样最著名的用例是找到代码中的热点。采样是最流行的分析方法，因为它不需要重新编译程序，并且运行时开销非常小。

* 通常，计数和采样会产生非常低的运行时开销（通常低于 2%）。一旦您开始在不同事件之间进行多路复用，计数就会变得更加昂贵（5-15% 的开销），采样会随着采样频率的增加而变得更加昂贵 [[@Nowak2014TheOO](../References.md#Nowak2014TheOO)]。考虑使用用户模式采样来分析长时间运行的工作负载或您不需要非常准确的数据时。

* Roofline 性能模型是一个面向吞吐量的性能模型，在高性能计算 (HPC) 领域得到了广泛使用。它允许绘制应用程序性能与硬件限制之间的关系图。Roofline 模型有助于识别性能瓶颈，指导软件优化，并跟踪优化进度。

* 有些工具试图静态分析代码的性能。此类工具模拟一段代码而不是执行它。这种方法存在许多限制和约束，但您会得到非常详细和低级别的报告作为回报。

* 编译器优化报告有助于发现丢失的编译器优化。这些报告还指导开发人员设计新的性能实验。


\sectionbreak
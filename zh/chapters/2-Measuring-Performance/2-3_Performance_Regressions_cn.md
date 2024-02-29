## 自动检测性能回归

软件供应商试图增加部署频率正在成为一种趋势。公司不断寻求加速产品上市的方式。不幸的是，这并不意味着每次新发布的软件产品都会变得更好。特别是，软件性能缺陷往往以惊人的速度泄漏到生产软件中[[@UnderstandingPerfRegress](../References.md#UnderstandingPerfRegress)]。在软件的演变过程中，大量的变化给分析所有这些结果和历史数据以检测性能回归带来了挑战。

软件性能回归是在软件从一个版本发展到另一个版本时错误地引入的缺陷。捕捉性能错误和改进意味着检测哪些提交改变了软件的性能（由性能测试测量），在测试基础设施的噪声存在的情况下。从数据库系统到搜索引擎再到编译器，几乎所有大规模软件系统在其持续演进和部署生命周期中都会经历性能回归。在软件开发过程中完全避免性能回归可能是不可能的，但通过适当的测试和诊断工具，可以显着减少这些缺陷悄然泄漏到生产代码中的可能性。

首先考虑的选择是：让人类查看图表并比较结果。毫不奇怪，我们很快就想要摆脱这个选择。人们往往很快失去注意力，可能会错过回归，特别是在嘈杂的图表上，例如图@fig:PerfRegress所示的图表。人类可能会捕捉到发生在8月5日左右的性能回归，但人们可能不会发现后续的回归。除了容易出错外，让人类参与其中还是一项耗时且枯燥的工作，必须每天进行。

![4个测试的性能趋势图，8月5日性能略有下降(值越高越好). *© Image from [ [@MongoDBChangePointDetection](../References.md#MongoDBChangePointDetection) ]*](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/measurements/PerfRegressions.png)<div id="PerfRegress"></div>

第二个选择是设置一个阈值，例如2%：认为性能在阈值内的每个代码修改都是噪声，而超过阈值的则被认为是回归。这比第一个选择要好一些，但仍然有其自身的缺点。性能测试中的波动是不可避免的：有时，甚至一个无害的代码更改[^3]也可能触发基准测试中的性能变化。选择正确的阈值极其困难，也不能保证低误报率和低漏报率。将阈值设置得太低可能会导致分析一堆并非由源代码更改引起而是由某些随机噪声引起的小型回归。将阈值设置得太高可能会过滤掉真正的性能回归。小的变化可能会逐渐积累成较大的回归，这可能会被忽视。例如，假设您设置了2%的阈值。如果有两次连续的1.5%的回归，它们都将被过滤掉。但是在两天内，性能回归将累积达到3%，这超过了阈值。通过观察图@fig:PerfRegress，我们可以得出一个观察结果，即阈值需要进行每个测试的调整。对于绿色（上线）测试有效的阈值未必对于紫色（下线）测试同样有效，因为它们具有不同级别的噪声。每个测试都需要设置明确的阈值值以警报回归的CI系统示例是[LUCI](https://chromium.googlesource.com/chromium/src.git/+/master/docs/tour_of_luci_ui.md)[^2]，它是Chromium项目的一部分。

第三个选择是使用统计分析来识别性能回归。一个简单的例子是使用[学生t检验](https://en.wikipedia.org/wiki/Student's_t-test)[^5]来比较程序A的100次运行的算术平均值与程序B的100次运行的算术平均值。然而，这样的参数化测试假设了正态（即高斯）样本分布，而通常情况下系统性能运行时直方图通常是右偏、多峰的，因此在这些情况下误用统计工具可能会产生误导性的结果。幸运的是，对于非正态分布存在更合适的统计工具，称为“非参数”测试，其示例包括Mann-Whitney(曼-惠特尼), Anderson-Darling(安德森-达林) 和 Kolmogorov–Smirnov(科尔莫戈洛夫-斯米尔诺夫)（下一节将详细介绍）。对于那些希望自己搭建自动化性能回归测试框架的人，Python和R提供了这些可下载的软件包，而像[stats-pal](https://github.com/JoeyHendricks/STATS-PAL)[^6]这样的开源项目提供了现成的框架，可插入现有的CI/CD流水线中。

在[[@MongoDBChangePointDetection](../References.md#MongoDBChangePointDetection)]中采用了一种更复杂的统计方法来识别性能回归。MongoDB开发人员实施了变点分析，以识别其数据库产品演变代码库中的性能变化。根据[[@ChangePointAnalysis](../References.md#ChangePointAnalysis)]，变点分析是在时间顺序观察中检测分布变化的过程。MongoDB开发人员利用了一种称为“E-Divisive means”的算法，该算法通过分层选择将时间序列划分为集群的分布变化点。他们的开源CI系统称为[Evergreen](https://github.com/evergreen-ci/evergreen)[^4]，并将此算法纳入其中以在图表上显示变点并打开Jira票据。有关此自动化性能测试系统的更多详细信息可以在[[@Evergreen](../References.md#Evergreen)]中找到。

[[@AutoPerf](../References.md#AutoPerf)]]中提出了另一种有趣的方法。本文作者提出了`AutoPerf`，它使用硬件性能计数器（PMC，见[[@sec:PMC](../3-CPU-Microarchitecture/3-9_PMU_cn.md#sec:PMC)]）来诊断修改程序中的性能回归。首先，它根据从原始程序收集的PMC配置文件数据来学习修改函数性能的分布。然后，它根据从修改后程序收集的PMC配置文件数据将性能的偏差检测为异常值。`AutoPerf`表明，这种设计可以有效地诊断一些最复杂的软件性能错误，例如隐藏在并行程序中的错误。

无论性能回归检测的底层算法如何，一个典型的CI系统应该自动执行以下操作：

1. 设置测试系统。
2. 运行基准测试套件。
3. 报告结果。
4. 确定性能是否发生了变化。
5. 对性能的意外变化发出警报。
6. 为人类分析结果可视化。

CI系统应支持自动化和手动基准测试，产生可重复的结果，并为发现的性能回归创建工单。及时检测回归非常重要。首先，因为自回归发生以来合并的变更较少。这使我们可以指定负责调查回归的人员在他们转移到其他任务之前解决问题。此外，对于开发人员来说，解决回归问题要容易得多，因为所有细节仍然新鲜在他们的脑海中，而不是在几周之后。

最后，CI系统不应仅仅在软件性能回归上发出警报，还应在性能改进方面发出意外警报。例如，有人可能提交了一个看似无害的提交，然而，在自动性能回归测试中，它将延迟减少了惊人的10%。您最初的直觉可能是庆祝这次幸运的性能提升并继续您的一天。然而，尽管此提交可能已通过CI流水线中的所有功能测试，但很有可能这个意外的延迟改进揭示了功能测试中的一个漏洞，这个漏洞只在性能回归结果中表现出来。这种情况经常发生，足以明确提及：将自动性能回归测试工具视为整体软件测试框架的一部分，而不是一个孤立的部分。

本书的作者强烈建议建立一个自动化的统计性能跟踪系统。尝试使用不同的算法，看看哪种对您的应用程序效果最好。这当然需要时间，但这将是对项目未来性能健康的坚实投资。

[^2]: LUCI - [https://chromium.googlesource.com/chromium/src.git/+/master/docs/tour_of_luci_ui.md](https://chromium.googlesource.com/chromium/src.git/+/master/docs/tour_of_luci_ui.md)
[^3]: 下面的文章表明，改变函数的顺序或删除死函数可能会导致性能变化: [https://easyperf.net/blog/2018/01/18/Code_alignment_issues](https://easyperf.net/blog/2018/01/18/Code_alignment_issues)
[^4]: Evergreen - [https://github.com/evergreen-ci/evergreen](https://github.com/evergreen-ci/evergreen)
[^5]: Student's t-test - [https://en.wikipedia.org/wiki/Student%27s_t-test](https://en.wikipedia.org/wiki/Student's_t-test)
[^6]: Stats-pal - [https://github.com/JoeyHendricks/STATS-PAL](https://github.com/JoeyHendricks/STATS-PAL)
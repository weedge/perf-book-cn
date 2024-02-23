## 使用 Coz 进行分析 {#sec:COZ}

在 [@sec:secAmdahl] 中，我们定义了识别影响多线程程序整体性能的代码部分的挑战。由于各种原因，优化多线程程序的一部分并不总是能带来明显效果。Coz: [https://github.com/plasma-umass/coz](https://github.com/plasma-umass/coz)[^16] 是一种新型的性能分析器，解决了这个问题，填补了传统软件性能分析器留下的空白。它使用一种称为“因果性能分析”的新技术，通过在应用程序运行期间虚拟地加速代码段来预测某些优化的整体效果，从而进行实验。它通过插入减慢所有其他同时运行代码的暂停来实现这些“虚拟加速”。[@CozPaper]

将 Coz 分析器应用于 Phoronix 测试套件: [https://www.phoronix-test-suite.com/](https://www.phoronix-test-suite.com/) 中的 C-Ray: [https://openbenchmarking.org/test/pts/c-ray](https://openbenchmarking.org/test/pts/c-ray) 基准的示例如图 @fig:CozProfile 所示。根据图表，如果我们将 c-ray-mt.c 中第 540 行的性能提高 20%，Coz 预计 C-Ray 基准整体应用程序性能将相应提高约 17%。一旦我们在这条线上的改进达到 ~45%，对其应用程序的影响就会根据 Coz 的估计开始趋于平缓。有关此示例的更多详细信息，请参阅 easyperf 博客上的文章: [https://easyperf.net/blog/2020/02/26/coz-vs-sampling-profilers](https://easyperf.net/blog/2020/02/26/coz-vs-sampling-profilers)[^17]。

![CozProfile 适用于 [C-Ray](https://openbenchmarking.org/test/pts/c-ray) 基准的 Coz 分析文件.](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/mt-perf/CozProfile.png){#fig:CozProfile width=70%}

[^16]: COZ 源代码 - [https://github.com/plasma-umass/coz](https://github.com/plasma-umass/coz)。
[^17]: 博客文章“COZ 与采样性能分析器” - [https://easyperf.net/blog/2020/02/26/coz-vs-sampling-profilers](https://easyperf.net/blog/2020/02/26/coz-vs-sampling-profilers)。

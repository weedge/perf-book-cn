# 性能分析中的术语和指标 {#sec:secMetrics}

像许多工程学科一样，性能分析在使用特殊术语和指标方面非常重要。对于初学者来说，查看由分析工具如Linux `perf`或Intel VTune Profiler生成的性能分析文件可能会感到非常困难。这些工具涉及许多复杂的术语和指标，但如果您打算进行任何严肃的性能工程工作，这些内容是“必须了解”的。

既然我们提到了Linux `perf`，让我们简要介绍一下这个工具，因为我们在本章和后续章节中有许多使用它的示例。Linux `perf`是一个性能分析器，您可以使用它来查找程序中的热点，收集各种低级CPU性能事件，分析调用堆栈等等。我们将在整本书中广泛使用Linux `perf`，因为它是最流行的性能分析工具之一。我们偏爱展示Linux `perf`的另一个原因是因为它是开源软件，这使得热衷的读者可以探索现代分析工具内部发生的机制。这对于学习本书中提出的概念特别有用，因为基于GUI的工具（如Intel® VTune™ Profiler）往往会隐藏所有复杂性。我们将在第7章中对Linux `perf`进行更详细的概述。

本章是对性能分析中使用的基本术语和指标的简要介绍。我们将首先定义诸如已退役/执行指令、IPC/CPI、$$\mu$$ops、核心/参考时钟、缓存失效和分支误预测等基本概念。然后，我们将看到如何测量系统的内存延迟和带宽，并介绍一些更高级的指标。最后，我们将对四种行业工作负载进行基准测试，并查看收集到的指标。
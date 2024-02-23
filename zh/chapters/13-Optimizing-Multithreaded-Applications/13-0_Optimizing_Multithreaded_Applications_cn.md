[TODO]:讨论日程安排问题(单独部分)

# 优化多线程应用 {#sec:secOptMTApps}

现代 CPU 每年都在增加越来越多的核心。截至 2020 年，你可以购买到一款 x86 服务器处理器，其核心数量超过 50 个！而拥有 8 个执行线程的中档台式机也是相当常见的配置。由于每个 CPU 中有如此强大的处理能力，如何高效利用所有的硬件线程成为了挑战。为了确保应用的未来成功，准备软件以便与不断增长的 CPU 核心数量良好地扩展非常重要。

多线程应用具有其自身的特点。在处理多个线程时，单线程执行的某些假设会失效。例如，我们不能再通过查看单个线程来识别热点，因为每个线程可能都有自己的热点。在流行的[生产者-消费者](https://en.wikipedia.org/wiki/Producer–consumer_problem)[^5]设计中，生产者线程可能大部分时间都在休眠。对这样一个线程进行分析不会揭示出我们的多线程应用为何扩展性不佳的原因。

[^5]: Producer-consumer pattern - [https://en.wikipedia.org/wiki/Producer-consumer_problem](https://en.wikipedia.org/wiki/Producer-consumer_problem)
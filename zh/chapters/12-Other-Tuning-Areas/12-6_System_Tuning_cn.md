## 系统调优 {#sec:SysTune}

在成功完成了利用 CPU 微架构所有复杂设施调整应用程序的所有艰苦工作之后，我们最不想看到的是系统固件、操作系统或内核破坏我们所有的努力。即使是最精细调整的应用程序，如果被系统管理中断 (SMI)（一种 BIOS 中断，用于停止整个操作系统以执行固件代码）间歇性地中断，也毫无意义。这样的中断每次可能会运行 10 到 100 毫秒。

公平地说，开发人员通常对应用程序执行环境几乎没有控制权。当我们交付产品时，不切实际地调整客户可能拥有的每个设置。通常，足够大的组织会有单独的运维团队来处理这类问题。尽管如此，与这些团队成员沟通时，了解还有哪些因素会限制应用程序表现出最佳性能是很重要的。

正如 [@sec:secFairExperiments] 所示，现代系统中有许多需要调整的地方，避免系统级干扰并非易事。基于 x86 的服务器部署的性能调优手册的一个例子是 Red Hat 的 指南: [https://access.redhat.com/sites/default/files/attachments/201501-perf-brief-low-latency-tuning-rhel7-v2.1.pdf](https://access.redhat.com/sites/default/files/attachments/201501-perf-brief-low-latency-tuning-rhel7-v2.1.pdf)[^5]。在那里，您将找到消除或显著减少缓存破坏中断的提示，这些中断来自系统 BIOS、Linux 内核和设备驱动程序等许多应用程序干扰源。这些指南应作为所有新服务器构建的基础映像，然后再将任何应用程序部署到生产环境中。

当涉及调整特定系统设置时，它并不总是简单的“是”或“否”答案。例如，您的应用程序是否会从其所在环境中启用的同步多线程 (SMT) 功能中受益，一开始并不清楚。一般指导原则是仅为 IPC 相对较低的异构工作负载[^6] 启用 SMT。另一方面，如今的 CPU 制造商提供具有如此高的内核数量的处理器，以至于 SMT 比过去少得多。然而，这只是一个通用指南，正如本书迄今强调的那样，最好是自己去测量。

大多数开箱即用的平台都配置为在可能的情况下优化吞吐量并节省电量。但是，有一些行业具有实时要求，它们更关心降低延迟而不是其他一切。这样的行业的一个例子是用于汽车装配线的机器人。此类机器人执行的动作由外部事件触发，并且通常有一个预定的时间预算来完成，因为下一个中断即将到来（通常称为“控制环路”）。满足此类平台的实时目标可能需要牺牲机器的整体吞吐量或允许其消耗更多能量。该领域流行的技术之一是禁用处理器睡眠状态[^7]，使其时刻准备立即做出反应。另一种有趣的方法称为缓存锁定，[^8] 其中 CPU 缓存的部分保留用于特定数据集；它有助于简化应用程序内的内存延迟。

[^5]: Red Hat 低延迟调优指南 - [https://access.redhat.com/sites/default/files/attachments/201501-perf-brief-low-latency-tuning-rhel7-v2.1.pdf](https://access.redhat.com/sites/default/files/attachments/201501-perf-brief-low-latency-tuning-rhel7-v2.1.pdf)
[^6]: 即，当兄弟线程执行不同的指令模式时
[^7]: 电源管理状态：P 状态、C 状态。详细信息请参见此处： [https://software.intel.com/content/www/us/en/develop/articles/power-management-states-p-states-c-states-and-package-c-states.html](https://software.intel.com/content/www/us/en/develop/articles/power-management-states-p-states-c-states-and-package-c-states.html).
[^8]: 缓存锁定。缓存锁定技术的调查 [[@CacheLocking](../References.md#CacheLocking)]。将缓存的一部分伪锁定的示例，然后将其作为 Linux 文件系统中的字符设备公开并可用于 `mmap`ing： [https://events19.linuxfoundation.org/wp-content/uploads/2017/11/Introducing-Cache-Pseudo-Locking-to-Reduce-Memory-Access-Latency-Reinette-Chatre-Intel.pdf](https://events19.linuxfoundation.org/wp-content/uploads/2017/11/Introducing-Cache-Pseudo-Locking-to-Reduce-Memory-Access-Latency-Reinette-Chatre-Intel.pdf).

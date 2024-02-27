## 并行效率指标 {#sec:secMT_metrics}

在处理多线程应用程序时，工程师们应该谨慎分析诸如 CPU 利用率和 IPC（见 [@sec:secMetrics]）等基本指标。某个线程可能表现出高 CPU 利用率和高 IPC，但实际上可能只是在一个锁上旋转。这就是为什么在评估应用程序的并行效率时，建议使用有效 CPU 利用率，该指标仅基于有效时间。[^12]

### 有效 CPU 利用率

该指标表示应用程序有效地利用了可用的 CPU。它显示了系统上所有逻辑 CPU 的平均 CPU 利用率百分比。CPU 利用率指标仅基于有效时间，不包括并行运行时系统[^11]和自旋时间引入的开销。100% 的 CPU 利用率意味着您的应用程序在运行期间始终使所有逻辑 CPU 内核保持忙碌[[@IntelCpuMetrics](../References.md#IntelCpuMetrics)]。

对于指定的时间间隔 T，可以计算有效 CPU 利用率如下：
$$
\textrm{Effective CPU Utilization} = \frac{\sum_{i=1}^{\textrm{ThreadsCount}}\textrm{Effective Cpu Time(T,i)}}{\textrm{T}~\times~\textrm{ThreadsCount}}
$$

### 线程数

应用程序通常具有可配置的线程数，这使它们能够在具有不同核心数的平台上有效运行。显然，使用比系统上可用的线程数少的线程来运行应用程序会浪费其资源。另一方面，运行过多的线程可能会导致较高的 CPU 时间，因为其中一些线程可能正在等待其他线程完成，或者时间可能被用于上下文切换。

除了实际的工作线程外，多线程应用程序通常还具有辅助线程：主线程、输入和输出线程等。如果这些线程消耗了大量时间，它们就需要专用的硬件线程。这就是为什么了解总线程数并正确配置工作线程数很重要。

为了避免线程创建和销毁的惩罚，工程师通常会分配一个[线程池](https://en.wikipedia.org/wiki/Thread_pool)[^14]，其中有多个线程等待由监督程序分配的任务以供并发执行。这对执行短暂任务特别有益。

### 等待时间

等待时间发生在软件线程由于阻塞或导致同步的 API 而等待时。等待时间是每个线程的；因此，总等待时间可能超过应用程序经过的时间[[@IntelCpuMetrics](../References.md#IntelCpuMetrics)]。

线程可以由于同步或抢占而被操作系统调度程序从执行中切换掉。因此，等待时间可以进一步分为同步等待时间和抢占等待时间。大量的同步等待时间很可能表明应用程序具有高度争用的同步对象。我们将在接下来的章节中探讨如何找到它们。显着的抢占等待时间可以表明线程过度订阅问题(oversubscription)[^13]，这可能是由于大量的应用程序线程或与操作系统线程或系统上其他应用程序的冲突引起的。在这种情况下，开发人员应考虑减少线程总数或增加每个工作线程的任务粒度。

### 自旋时间

自旋时间是 CPU 忙于等待时间。当软件线程等待时，这种情况经常发生，因为同步 API 导致 CPU 轮询[[@IntelCpuMetrics](../References.md#IntelCpuMetrics)]。实际上，内核同步原语的实现更倾向于在一段时间内锁定旋转，而不是立即进行线程上下文切换（这是昂贵的）。然而，过多的自旋时间可能反映了无法进行有效工作的机会的丧失。

[^11]: 类似 `pthread`、`OpenMP` 和 `Intel TBB` 等线程库和 API 具有它们自己的线程创建和管理开销。
[^12]: 诸如 Intel VTune Profiler 等性能分析工具可以区分在线程旋转时采集的分析样本。它们通过为每个样本提供调用堆栈来完成这项工作（见 [[@sec:secCollectCallStacks](../5-Performance-Analysis-Approaches/5-5_Sampling_cn.md#sec:secCollectCallStacks)]）。
[^13]: 线程过度订阅 - [https://software.intel.com/en-us/vtune-help-thread-oversubscription](https://software.intel.com/en-us/vtune-help-thread-oversubscription)。
[^14]: 线程池 - [https://en.wikipedia.org/wiki/Thread_pool](https://en.wikipedia.org/wiki/Thread_pool)。

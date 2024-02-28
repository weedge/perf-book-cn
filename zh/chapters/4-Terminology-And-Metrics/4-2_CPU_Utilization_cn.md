## CPU利用率

CPU利用率是在一段时间内CPU处于忙碌状态的百分比。从技术上讲，当CPU不运行内核的`idle`线程时，CPU被认为是被利用的。

$$
CPU~Utilization = \frac{CPU\_CLK\_UNHALTED.REF\_TSC}{TSC},
$$

其中，`CPU_CLK_UNHALTED.REF_TSC` 计算了核心处于非停顿状态时的参考周期数，`TSC` 代表时间戳计数器（在[@sec:timers]中讨论过），它始终在运行。

如果CPU利用率低，通常意味着应用程序性能较差，因为CPU浪费了一部分时间。然而，高CPU利用率并不总是好性能的指标。这仅仅是系统正在进行一些工作的迹象，但并不表示正在做什么：即使CPU由于等待内存访问而被阻塞，它仍然可能被高度利用。在多线程环境中，线程在等待资源继续进行时也可以自旋。稍后在[@sec:secMT_metrics]中，我们将讨论并行效率指标，特别是"有效CPU利用率"，该指标过滤了自旋时间。

Linux `perf`会自动计算系统上所有CPU的CPU利用率：

```bash
$ perf stat -- a.exe
  0.634874  task-clock (msec) #    0.773 CPUs utilized   
```
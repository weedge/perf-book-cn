## 附录 A. 减少测量噪声(Reducing Measurement Noise) 

\markright{附录 A}

以下是一些示例功能，它们可能导致性能测量的不确定性增加。有关完整讨论，请参见 [@sec:secFairExperiments]。

## 动态频率缩放(Dynamic Frequency Scaling) 

动态频率缩放 (DFS): [https://en.wikipedia.org/wiki/Dynamic_frequency_scaling](https://en.wikipedia.org/wiki/Dynamic_frequency_scaling)[^11] 是一种通过在运行要求苛刻任务时自动提高 CPU 运行频率来提升系统性能的技术。例如，英特尔 CPU 具有名为 睿频加速: [https://en.wikipedia.org/wiki/Intel_Turbo_Boost](https://en.wikipedia.org/wiki/Intel_Turbo_Boost)[^1] 的 DFS 实现功能，AMD CPU 则采用 Turbo Core: [https://en.wikipedia.org/wiki/AMD_Turbo_Core](https://en.wikipedia.org/wiki/AMD_Turbo_Core)[^2] 功能。

以下示例展示了睿频加速对在 Intel® Core™ i5-8259U 上运行单线程工作负载的影响：

```bash
# 睿频加速启用
$ cat /sys/devices/system/cpu/intel_pstate/no_turbo
0
$ perf stat -e task-clock,cycles -- ./a.exe 
    11984.691958  task-clock (msec) #    1.000 CPUs utilized
  32,427,294,227  cycles            #    2.706 GHz
      11.989164338 seconds time elapsed

# 睿频加速禁用
$ echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
1
$ perf stat -e task-clock,cycles -- ./a.exe 
    13055.200832  task-clock (msec) #    0.993 CPUs utilized
  29,946,969,255  cycles            #    2.294 GHz
      13.142983989 seconds time elapsed
```

当睿频加速启用时，平均频率明显更高。

DFS 可以永久地在 BIOS 中禁用。[^3] 要在 Linux 系统上以编程方式禁用 DFS 功能，您需要 root 权限。下面是如何实现这一点：

```bash
# 英特尔
echo 1 > /sys/devices/system/cpu/intel_pstate/no_turbo
# AMD
echo 0 > /sys/devices/system/cpu/cpufreq/boost
```

## 同时多线程(Simultaneous Multithreading) 

现代 CPU 内核通常采用 同时多线程 (SMT): [https://en.wikipedia.org/wiki/Simultaneous_multithreading](https://en.wikipedia.org/wiki/Simultaneous_multithreading)[^4] 方式制造。这意味着在一个物理内核中，您可以同时执行两个线程。通常，体系结构状态: [https://en.wikipedia.org/wiki/Architectural_state](https://en.wikipedia.org/wiki/Architectural_state)[^5] 会被复制，但执行资源（ALU、缓存等）不会。这意味着如果我们在同一个内核上以“同时”方式运行两个独立的进程（在不同的线程中），它们会相互争夺资源，例如缓存空间。

SMT 可以永久地在 BIOS 中禁用。[^6] 要在 Linux 系统上以编程方式禁用 SMT，您需要 root 权限。下面是如何在每个内核中关闭一个兄弟线程：

```bash
echo 0 > /sys/devices/system/cpu/cpuX/online
```

可以在以下文件中找到 CPU 线程的兄弟对：

```bash
/sys/devices/system/cpu/cpuN/topology/thread_siblings_list
```

例如，在具有 4 个内核和 8 个线程的 Intel® Core™ i5-8259U 上：

```bash
# 所有 8 个硬件线程均已启用：
$ lscpu
...
CPU(s):              8
On-line CPU(s) list: 0-7
...
$ cat /sys/devices/system/cpu/cpu0/topology/thread_siblings_list
0,4
$ cat /sys/devices/system/cpu/cpu1/topology/thread_siblings_list
1,5
$ cat /sys/devices/system/cpu/cpu2/topology/thread_siblings_list
2,6
$ cat /sys/devices/system/cpu/cpu3/topology/thread_siblings_list
3,7

# 在内核 0 上禁用 SMT
$ echo 0 | sudo tee /sys/devices/system/cpu/cpu4/online
0
$ lscpu
CPU(s):               8
On-line CPU(s) list:  0-3,5-7
Off-line CPU(s) list: 4
...
$ cat /sys/devices/system/cpu/cpu0/topology/thread_siblings_list
0
```

## 缩放调速器(Scaling Governor) 

Linux内核可以控制 CPU 频率用于不同的目的。其中一个目的是节能，在这种情况下，Linux内核内部的调速器[^7] 可以决定降低 CPU 运行频率。对于性能测量，建议将调速器策略设置为“性能”，以避免低于标称时钟频率。下面是如何将其设置为所有内核：

```bash
for i in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
do
  echo performance > $i
done
```

## CPU 亲和性(CPU Affinity) 

处理器亲和性: [https://en.wikipedia.org/wiki/Processor_affinity](https://en.wikipedia.org/wiki/Processor_affinity)[^8] 允许将进程绑定到特定 CPU 内核。在 Linux 中，可以使用 `taskset`: [https://linux.die.net/man/1/taskset](https://linux.die.net/man/1/taskset)[^9] 工具实现这一点。这里 

```bash
# 无亲和性
$ perf stat -e context-switches,cpu-migrations -r 10 -- a.exe
               151      context-switches
                10      cpu-migrations

# 进程绑定到 CPU0
$ perf stat -e context-switches,cpu-migrations -r 10 -- taskset -c 0 a.exe 
               102      context-switches
                 0      cpu-migrations
```
请注意，`cpu-migrations` 的数量变为 `0`，即进程永远不会离开 `core0`。

或者，您可以使用 cset: [https://github.com/lpechacek/cpuset](https://github.com/lpechacek/cpuset)[^10] 工具仅为要基准测试的程序预留 CPU。如果使用 `Linux perf`，请至少保留两个内核，以便 `perf` 在一个内核上运行，您的程序在另一个内核上运行。以下命令将从 N1 和 N2 中移动所有线程（`-k on` 表示即使内核线程也会被移动出去）：

```bash
$ cset shield -c N1,N2 -k on
```

以下命令将在隔离的 CPU 上运行 `--` 后面的命令：
```bash
$ cset shield --exec -- perf stat -r 10 <cmd>
```

## 进程优先级(Process Priority) 

在 Linux 中，可以使用 `nice` 工具提高进程优先级。通过提高优先级，进程可以获得更多 CPU 时间，并且 Linux 调度器会比具有正常优先级的进程更青睐它。优先级范围从 `-20`（最高优先级值）到 `19`（最低优先级值），默认值为 `0`。

请注意在上一个示例中，基准测试进程的执行被操作系统中断超过 100 次。如果我们通过使用 `sudo nice -n -N` 运行基准测试来提高进程优先级：
```bash
$ perf stat -r 10 -- sudo nice -n -5 taskset -c 1 a.exe
    0   context-switches
    0   cpu-migrations
```
请注意，上下文切换的数量变为 `0`，因此该进程不间断地接收所有计算时间。

## 文件系统缓存(Filesystem Cache) 

通常，会分配一部分主内存来缓存文件系统内容，包括各种数据。这减少了应用程序访问磁盘的次数。以下示例说明了文件系统缓存如何影响简单 `git status` 命令的运行时间：

```bash
# 清空文件系统缓存
$ echo 3 | sudo tee /proc/sys/vm/drop_caches && sync && time -p git status
real 2,57
# 预热文件系统缓存
$ time -p git status
real 0,40
```

可以通过运行以下两个命令清除当前的文件系统缓存：

```bash
$ echo 3 | sudo tee /proc/sys/vm/drop_caches
$ sync
```

或者，您可以进行一次干运行以预热文件系统缓存，并将其排除在测量之外。此干运行可以与基准测试输出的验证结合使用。

[^1]: 英特尔睿频加速 - [https://en.wikipedia.org/wiki/Intel_Turbo_Boost](https://en.wikipedia.org/wiki/Intel_Turbo_Boost).
[^2]: AMD Turbo Core - [https://en.wikipedia.org/wiki/AMD_Turbo_Core](https://en.wikipedia.org/wiki/AMD_Turbo_Core).
[^3]: 英特尔睿频加速常见问题解答 - [https://www.intel.com/content/www/us/en/support/articles/000007359/processors/intel-core-processors.html](https://www.intel.com/content/www/us/en/support/articles/000007359/processors/intel-core-processors.html).
[^4]: SMT - [https://en.wikipedia.org/wiki/Simultaneous_multithreading](https://en.wikipedia.org/wiki/Simultaneous_multithreading).
[^5]: 体系结构状态 - [https://en.wikipedia.org/wiki/Architectural_state](https://en.wikipedia.org/wiki/Architectural_state).
[^6]: “如何禁用超线程” - [https://www.pcmag.com/article/314585/how-to-disable-hyperthreading](https://www.pcmag.com/article/314585/how-to-disable-hyperthreading).
[^7]: Linux CPU 频率调节器文档：[https://www.kernel.org/doc/Documentation/cpu-freq/governors.txt](https://www.kernel.org/doc/Documentation/cpu-freq/governors.txt).
[^8]: 处理器关联性 - [https://en.wikipedia.org/wiki/Processor_affinity](https://en.wikipedia.org/wiki/Processor_affinity).
[^9]: `taskset` 手册 - [https://linux.die.net/man/1/taskset](https://linux.die.net/man/1/taskset).
[^10]: `cpuset` 手册 - [https://github.com/lpechacek/cpuset](https://github.com/lpechacek/cpuset).
[^11]: 动态频率缩放 - [https://en.wikipedia.org/wiki/Dynamic_frequency_scaling](https://en.wikipedia.org/wiki/Dynamic_frequency_scaling).

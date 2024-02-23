## Linux Perf

Linux Perf 是世界上使用最广泛的性能分析器之一，因为它可以在大多数 Linux发行版上使用，这使其适用于广泛的用户。Perf 在许多流行的 Linux 发行版中都原生支持，包括 Ubuntu、Red Hat、Debian 等。它包含在内核中，因此您可以在任何运行 Linux 的系统上获取操作系统级别的统计信息（页面错误、cpu 迁移等）。截至 2023年中期，该分析器支持 x86、ARM、PowerPC64、UltraSPARC 和其他一些架构。[^2] 这允许访问硬件性能监控功能，例如性能计数器。有关 Linux `perf` 的更多信息，请访问其维基页面 [^1]。

### 如何配置它 {.unlisted .unnumbered}

安装 Linux perf 非常简单，只需一个命令即可完成：

```bash
$ sudo apt-get install linux-tools-common linux-tools-generic linux-tools-`uname -r`
```

另外，除非安全是您关注的问题，否则请考虑更改以下默认设置：

```bash
# 允许非特权用户进行内核分析和访问 CPU 事件
$ echo 0 | sudo tee /proc/sys/kernel/perf_event_paranoid
$ sudo sh -c 'echo kernel.perf_event_paranoid=0 >> /etc/sysctl.d/local.conf'
# 启用内核模块符号解析以供非特权用户使用
$ echo 0 | sudo tee /proc/sys/kernel/kptr_restrict
$ sudo sh -c 'echo kernel.kptr_restrict=0 >> /etc/sysctl.d/local.conf'
```

### 它能做什么？ {.unlisted .unnumbered}

通常，Linux `perf` 可以完成其他分析器所能做的大多数事情。硬件供应商优先在 Linux `perf` 中启用他们的功能。因此，当新的 CPU 上市时，`perf` 已经支持它了。大多数用户将使用两个主要命令：`perf stat` 和 `perf record + perf report`。第一个以计数模式收集性能事件的绝对数量，第二个以采样模式分析应用程序或系统。

`perf record` 命令的输出是原始的示例转储。许多工具构建在 Linux `perf` 之上，用于解析转储文件并提供新的分析类型。以下是其中最值得注意的：

- 火焰图，参见下一节。
- KDAB Hotspot: [https://github.com/KDAB/hotspot](https://github.com/KDAB/hotspot)，[^3] 一个使用与 Intel Vtune 非常相似的界面可视化 Linux `perf` 数据的工具。如果您使用过 Intel Vtune，KDAB Hotspot 将会非常熟悉。有些人将其用作 Intel Vtune 的替代品。
- Netflix Flamescope: [https://github.com/Netflix/flamescope](https://github.com/Netflix/flamescope)，[^4] 显示应用程序运行时采样事件的热图。您可以观察负载行为的不同阶段和模式。Netflix 工程师使用此工具发现了一些非常微妙的性能漏洞。此外，您可以在热图上选择一个时间范围并仅为此时间范围生成火焰图。

### 它不能做什么？ {.unlisted .unnumbered}

Linux perf 是一个命令行工具，缺乏 GUI，这使得过滤数据、观察工作负载行为随时间如何变化、放大运行时的一部分等变得困难。通过 `perf report` 命令提供了有限的控制台输出，这对于快速分析来说已经足够，但不如其他 GUI 分析器方便。幸运的是，正如我们刚才提到的，有一些 GUI 工具可以对 Linux `perf` 的原始输出进行后处理和可视化。

[^1]: Linux perf wiki - [https://perf.wiki.kernel.org/index.php/Main_Page](https://perf.wiki.kernel.org/index.php/Main_Page).
[^2]: RISCV 目前还不作为官方内核的一部分支持，尽管存在供应商的自定义工具。
[^3]: KDAB Hotspot - [https://github.com/KDAB/hotspot](https://github.com/KDAB/hotspot).
[^4]: Netflix Flamescope - [https://github.com/Netflix/flamescope](https://github.com/Netflix/flamescope).

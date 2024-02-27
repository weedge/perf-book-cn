## 性能监控单元 {#sec:PMU}

每个现代CPU都提供了监控性能的设施，这些设施被合并到了性能监控单元（PMU）中。该单元集成了帮助开发人员分析其应用程序性能的功能。一个现代Intel CPU中的PMU示例如图@fig:PMU所示。大多数现代PMU都有一组性能监控计数器（PMC），可用于收集程序执行过程中发生的各种性能事件。稍后在[@sec:counting]中，我们将讨论如何使用PMC进行性能分析。此外，PMU还具有其他增强性能分析的功能，如LBR、PEBS和PT，[@sec:PmuChapter]专门讨论了这个话题。

[TODO]: 此图中使用的字体大小对于舒适阅读来说太小了。

![现代Intel CPU的性能监控单元。](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/uarch/PMC.png){#fig:PMU width=70%}

随着每一代CPU设计的演进，它们的PMU也在发展。在Linux上，可以使用`cpuid`命令确定CPU中PMU的版本，如[@lst:QueryPMU]所示。类似的信息可以通过检查`dmesg`命令的输出从内核消息缓冲区中提取。每个Intel PMU版本的特性，以及与上一个版本的变化，可以在[[@IntelOptimizationManual](../References.md#IntelOptimizationManual), Volume 3B, Chapter 20]中找到。

查询您的PMU的列表:

```bash
$ cpuid
...
Architecture Performance Monitoring Features (0xa/eax):
      version ID                               = 0x4 (4)
      number of counters per logical processor = 0x4 (4)
      bit width of counter                     = 0x30 (48)
...
Architecture Performance Monitoring Features (0xa/edx):
      number of fixed counters    = 0x3 (3)
      bit width of fixed counters = 0x30 (48)
...
```

### 性能监控计数器 {#sec:PMC}

如果我们想象一下对处理器的简化视图，它可能看起来像图@fig:PMC所示的样子。正如我们在本章前面讨论过的，现代CPU具有缓存、分支预测器、执行流水线和其他单元。当连接到多个单元时，PMC可以从中收集有趣的统计信息。例如，它可以计算经过了多少个时钟周期，执行了多少条指令，在此期间发生了多少缓存失效或分支预测错误等性能事件。

![带有性能监控计数器的CPU的简化视图。](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/uarch/PMC.png){#fig:PMC width=60%}

通常，PMC的宽度为48位，这使得分析工具能够在不中断程序执行的情况下运行很长时间[^2]。性能计数器是作为模型特定寄存器（MSR）实现的硬件寄存器。这意味着计数器的数量和它们的宽度会因型号而异，您不能依赖于在您的CPU中的相同数量的计数器。您应该始终首先查询它，例如使用`cpuid`等工具。PMC可以通过`RDMSR`和`WRMSR`指令访问，这些指令只能在内核空间执行。幸运的是，只有当您是性能分析工具的开发人员时，才需要关注这一点，例如Linux perf或Intel Vtune分析器。这些工具处理了编程PMC的所有复杂性。

当工程师分析他们的应用程序时，他们通常会收集已执行的指令数和经过的周期数。这就是为什么一些PMU具有专用的PMC用于收集这些事件的原因。固定计数器始终在CPU核心内部测量相同的事物。对于可编程计数器，用户可以选择要测量的内容。

例如，在Intel Skylake架构（PMU版本4，参见[@lst:QueryPMU]），每个物理核心有三个固定计数器和八个可编程计数器。这三个固定计数器分别设置为计算核心时钟、参考时钟和已退休指令（有关这些指标的更多详细信息，请参见[@sec:secMetrics]）。AMD Zen4和ARM Neoverse V1核心每个处理器核心支持6个可编程性能监控计数器，没有固定计数器。

PMU提供了100多种可用于监控的事件并不罕见。图@fig:PMU仅显示了现代Intel CPU上供监控的性能事件的一小部分。不难注意到可用PMC的数量远远小于性能事件的数量。无法同时计算所有事件，但是分析工具通过在程序执行期间在性能事件组之间进行复用来解决此问题（参见[@sec:secMultiplex]）。

- 对于Intel CPU，可以在[[@IntelOptimizationManual](../References.md#IntelOptimizationManual), Volume 3B, Chapter 20]中找到性能事件的完整列表，或者在[perfmon-events.intel.com](https://perfmon-events.intel.com/)上找到。
- AMD并不为每个AMD处理器发布性能监控事件的列表。感兴趣的读者可以在Linux perf源代码中找到一些信息[代码](https://github.com/torvalds/linux/blob/master/arch/x86/events/amd/core.c)[^3]。此外，您可以使用AMD uProf命令行工具列出可用于监控的性能事件。有关AMD性能计数器的一般信息，请参见[[@AMDProgrammingManual](../References.md#AMDProgrammingManual), 13.2 Performance Monitoring Counters]。
- 对于ARM芯片，性能事件没有如此明确定义。供应商按照ARM架构实

现核心，但性能事件的含义和支持的事件在很大程度上变化。对于由ARM自己设计的ARM Neoverse V1处理器，性能事件的列表可以在[[@ARMNeoverseV1](../References.md#ARMNeoverseV1)]中找到。

[^2]: 当PMC的值溢出时，必须中断程序的执行。然后，软件应该保存溢出的事实。我们稍后将详细讨论它。
[^3]: AMD核心的Linux源代码 - [https://github.com/torvalds/linux/blob/master/arch/x86/events/amd/core.c](https://github.com/torvalds/linux/blob/master/arch/x86/events/amd/core.c)
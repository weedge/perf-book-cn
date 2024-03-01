## AMD uProf

[AMD uProf](https://www.amd.com/en/developer/uprof.html) 是由 AMD 开发的一款用于监视在 AMD 处理器上运行的应用程序性能的工具。虽然 uProf 也可以用于 Intel 处理器，但你只能使用 CPU 无关的功能。该分析器可以免费下载，并可在 Windows、Linux 和 FreeBSD 上使用。AMD uProf 可用于在多个虚拟机（VM）上进行分析，包括 Microsoft Hyper-V、KVM、VMware ESXi、Citrix Xen，但并非所有 VM 上的所有功能都可用。此外，uProf 还支持分析使用各种语言编写的应用程序，包括 C、C++、Java、.NET/CLR。

### 如何配置 

在 Linux 上，uProf 使用 Linux perf 进行数据收集。在 Windows 上，uProf 使用自己的采样驱动程序，在安装 uProf 时会安装该驱动程序，无需额外配置。AMD uProf 支持命令行界面（CLI）和图形界面（GUI）。CLI 界面需要两个单独的步骤 - 收集和报告，类似于 Linux perf。

### 可以做什么 

- 找到热点：函数、语句、指令。
- 监视各种硬件性能事件并定位发生这些事件的代码行。
- 为特定函数或线程过滤数据。
- 观察工作负载的行为随时间的变化：在时间轴图中查看各种性能事件。
- 分析热门调用路径：调用图、火焰图和自下而上图表。

此外，uProf 还可以监视 Linux 上的各种 OS 事件 - 线程状态、线程同步、系统调用、页面错误等。它还允许分析 OpenMP 应用程序以检测线程不平衡，并分析 MPI 应用程序以检测 MPI 群集节点之间的负载不平衡。关于 uProf 各种功能的更多详细信息可在[用户指南](https://www.amd.com/en/developer/uprof.html#documentation)[^1]中找到。

### 不能做什么 

由于工具的采样性质，它最终会错过持续时间非常短的事件。报告的样本是统计估算的数字，大多数情况下足以分析性能，但不是事件的精确计数。

### 示例 

为了展示 AMD uProf 工具的外观和感觉，我们在 AMD Ryzen 9 7950X、Windows 11、64 GB RAM 上运行了 [Scimark2](https://math.nist.gov/scimark2/index.html)[^2] 基准测试中的密集 LU 矩阵分解组件。

图 [@fig:uProfHotspots](#uProfHotspots) 显示了函数热点分析。在图像的顶部，你可以看到事件时间轴，显示了在应用程序执行的不同时间观察到的事件数量。在右侧，你可以选择要绘制的指标，我们选择了 `RETIRED_BR_INST_MISP`。注意在时间范围从 20s 到 40s 的分支误判的峰值。你可以选择该区域以密切分析那里发生了什么。一旦你这样做了，它将更新底部面板，仅显示该时间间隔的统计信息。

![uProf 的函数热点视图。](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/perf-tools/uProf_Hopspot.png)<div id="uProfHotspots width=100%"></div>

在时间轴图下方，你可以看到一系列热点函数，以及相应的采样性能事件和计算的指标。事件计数可以显示为：样本计数、原始事件计数和百分比。有许多有趣的数字可以查看，然而，我们不会深入分析，但鼓励读者找出分支误判的性能影响并找到其源头。

在函数表下面，你可以看到所选函数在函数表中的自底向上调用栈视图。正如我们所见，所选的 `LU_factor` 函数是从 `kernel_measureLU` 被调用的，而 `kernel_measureLU` 又是从 `main` 被调用的。在 Scimark2 基准测试中，这是 `LU_factor` 的唯一调用栈，即使它显示了 `Call Stacks [5]`，这是可以忽略的采集工件。但在其他应用程序中，热点函数可以从许多不同的位置调用，因此你可能还想检查其他调用栈。

如果你双击任何函数，uProf 将打开该函数的源代码/汇编视图。为了简洁起见，我们不显示此视图。在左侧面板上，还有其他视图可用，如指标、火焰图、调用图

视图和线程并发。它们也对分析很有用，但我们决定跳过它们。读者可以自行尝试并查看这些视图。

[^1]: AMD uProf 用户指南 - [https://www.amd.com/en/developer/uprof.html#documentation](https://www.amd.com/en/developer/uprof.html#documentation)
[^2]: Scimark2 - [https://math.nist.gov/scimark2/index.html](https://math.nist.gov/scimark2/index.html)
## Apple Xcode Instruments

在 MacOS 上进行初始性能分析最方便的方法是使用 Instruments。它是一个应用程序性能分析器和可视化工具，与 Xcode 一起免费提供。Instruments 建立在从 Solaris 移植到 MacOS 的 DTrace 追踪框架之上。Instruments 拥有许多工具，可用于检查应用程序的性能，并允许我们执行大多数其他性能分析器（如 Intel Vtune）可以执行的基本操作。获取分析器的最简单方法是从 Apple AppStore 安装 Xcode。该工具无需配置，安装后即可立即使用。

在 Instruments 中，你可以使用专门的工具（称为 instruments）来跟踪应用程序、进程和设备的不同方面的情况随时间的变化。Instruments 拥有强大的可视化机制。它在进行分析时收集数据，并实时向你展示结果。你可以收集不同类型的数据，并将它们并排显示，这使你可以看到执行中的模式，相关系统事件，并发现非常微妙的性能问题。

在本章中，我们只展示了“CPU 计数器”工具，这是本书最相关的工具之一。Instruments 还可以可视化 GPU、网络和磁盘活动，跟踪内存分配和释放，捕获用户事件（如鼠标点击），提供关于功耗效率的见解等。关于这些用例的更多信息可以在 Instruments 的[文档](https://help.apple.com/instruments/mac/current)[^1]中找到。

### 你可以用它做什么 {.unlisted .unnumbered}

- 访问 Apple M1 和 M2 处理器上的硬件性能计数器
- 找到程序中的热点以及调用栈
- 与源代码并排检查生成的 ARM 汇编代码
- 为时间轴上的选定区间筛选数据

### 你不能用它做什么 {.unlisted .unnumbered}

[TODO]: 它是否具有与 Vtune 和 uProf 相同的盲点？

### 示例：编译 Clang {.unlisted .unnumbered}

正如我们所宣传的那样，在此示例中，我们将展示如何在搭载 M1 处理器的 Apple Mac mini 上，macOS 13.5.1 Ventura，16 GB RAM 上收集 HW 性能计数器。我们选取了 LLVM 代码库中最大的文件之一，并使用 Clang C++ 编译器版本 15.0 对其进行编译。以下是我们将要进行分析的命令行：

```bash
$ clang++ -O3 -DNDEBUG -arch arm64 <other options ...> -c llvm/lib/Transforms/Vectorize/LoopVectorize.cpp
```

首先，打开 Instruments 并选择 “CPU 计数器” 分析类型。（这里我们需要稍微提前一点）。它将打开主时间轴视图，如图 @fig:InstrumentsView 所示，准备开始分析。但在开始之前，让我们配置收集。单击并按住红色目标图标 \circled{1}，然后选择 “Recording Options...” 菜单。它将显示如图 @fig:InstrumentsDialog 所示的对话框窗口。在这里，你可以为收集添加 HW 性能监视事件。

![Xcode Instruments：CPU 计数器选项。](../../img/perf-tools/XcodeInstrumentsDialog.png){#fig:InstrumentsDialog width=50% }

据我们所知，Apple 没有在线记录他们的 HW 性能监视事件，但他们在 `/usr/share/kpep` 中提供了一些带有最小描述的事件列表。有 `plist` 文件，你可以将其转换为 json。例如，对于 M1 处理器，可以运行：

```bash
$ plutil -convert json /usr/share/kpep/a14.plist -o a14.json
```

然后使用简单的文本编辑器打开 `a14.json`。

第二步是设置分析目标。要做到这一点，单击并按住应用程序的名称（在图 @fig:InstrumentsView 中标记为 \circled{2}），然后选择你感兴趣的应用程序，如果需要，设置参数和环境变量。现在，你已经准备好开始收集了，请按红色目标图标 \circled{1}。

![Xcode Instruments：时间轴和统计面板。](../../img/perf-tools/XcodeInstrumentsView.jpg){#fig:InstrumentsView width=100% }

Instruments 显示一个时间轴，并不断更新有关正在运行的应用程序的统计信息。一旦程序完成，Instruments 将显示类似于图 @fig:InstrumentsView 所示的图像。编译花费了 7.3 秒，我们可以看到事件量随时间的变化。例如，分支错误预测在运行时末尾变得更加明显。你可以放大时间轴上的该区间，以检查所涉及的函数。

底部面板显示了数值统计信息。要检查类似于 Intel Vtune 的自下而上视图的热点，选择菜单 \circled{3} 中的 “Profile”，然后单击菜单 \circled{4} 中的 “Call Tree” 并选中 “Invert Call Tree” 复选框。这正是我们在图 @fig:InstrumentsView 中所做的。

Instruments 显示原始计数以及相对于总数的百分比，如果你想计算次要指标（如 IPC、MPKI 等），则非常有用。在右侧，我们有函数 `llvm::FoldingSetBase::FindNodeOrInsertPos` 的热调用栈。如果你双击一个函数，则可以查看为源代码生成的 ARM 汇编指令。

据我们所知，MacOS 平台上没有类似质量的替代性分析工具。高级用户可以通过编写简短（或长）的命令行脚本来使用 `dtrace` 框架本身，但这超出了本书的范围。

[^1]: Instruments 文档 - [https://help.apple.com/instruments/mac/current](https://help.apple.com/instruments/mac/current)
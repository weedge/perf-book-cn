[TODO]:可能成为附录的候选人

## Windows 事件跟踪

微软开发了一项名为 Windows 事件跟踪 (ETW) 的系统级跟踪功能。它最初旨在帮助设备驱动程序开发人员，但后来也发现它可以用于分析通用应用程序。ETW 在所有受支持的 Windows 平台（x86、x64 和 ARM）上可用，并提供相应的平台相关安装包。ETW 以结构化事件的形式记录用户和内核代码，并支持完整的调用堆栈跟踪，允许观察运行系统中的软件动态并解决许多棘手的性能问题。

### 如何配置它

从 Windows 10 开始，使用 `Wpr.exe` 可以录制 ETW 数据，无需任何额外下载。但是要启用系统范围的分析，您必须是管理员并启用 `SeSystemProfilePrivilege`。Windows 性能记录器工具支持一组内置录制配置文件，适用于常见性能问题。您可以通过创作带有 `.wprp` 扩展名的自定义性能记录器配置文件 XML 文件来定制您的录制需求。

如果您不仅想要录制还想查看录制的 ETW 数据，则需要安装 Windows Performance Toolkit (WPT)。您可以从 Windows SDK[^1] 或 ADK[^2] 下载页面下载 Windows Performance Toolkit。Windows SDK 体积庞大，您不一定需要所有部分。在我们的例子中，我们只勾选了 Windows Performance Toolkit 的复选框。您可以将 WPT作为您自己应用程序的一部分进行再分发。

### 你能用它做什么：

- 查看 CPU 热点，可配置的 CPU 采样率从 125 微秒到 10 秒。默认为 1 毫秒，运行时开销约为 5-10%。
- 哪个线程阻塞了某个线程以及阻塞了多长时间（例如，延迟事件信号、不必要的线程睡眠等）。
- 检查磁盘处理读/写请求的速度以及谁启动了这项工作。
- 检查文件访问性能和模式（包括导致没有磁盘 I/O 的缓存读/写）。
- 跟踪 TCP/IP 堆栈如何如何在网络接口和计算机之间传输数据包。

上述所有项目都在系统范围内记录所有进程，并具有可配置的调用堆栈跟踪（内核和用户模式调用堆栈结合）。您还可以添加自己的 ETW 提供程序，将系统范围的跟踪与您的应用程序行为关联起来。您可以通过检测您的代码来扩展收集的数据量。例如，您可以在源代码中的函数中添加注入进入/离开 ETW 跟踪钩子，以测量特定方法的执行频率。

### 你不能用它做什么：

- 检查 CPU 微架构瓶颈。为此，请使用特定于供应商的工具，例如 Intel VTune、AMD uProf、Apple Instruments 等。

ETW 跟踪捕获了所有进程在系统级别的动态，这很棒，但它可能会生成大量数据。例如，捕获线程上下文切换数据以观察各种等待和延迟很容易在每分钟生成 1-2 GB 的数据。这就是为什么不实际录制大量事件数小时而不覆盖之前存储的跟踪的原因。

## 记录 ETW 跟踪的工具

以下是一些可以用来捕获 ETW 跟踪的工具列表：

- `wpr.exe`：命令行录制工具，它是 Windows 10 和 Windows Performance Toolkit 的一部分。
- `WPRUI.exe`：一个用于录制 ETW 数据的简单 UI，它是 Windows Performance Toolkit 的一部分。
- `xperf`：wpr 的命令行前身，是 Windows Performance Toolkit 的一部分。
- `PerfView`：[^3] 一个图形化录制和分析工具，主要关注 .NET 应用程序。由微软开源。
- `Performance HUD`：[^7] 一个鲜为人知但功能非常强大的 GUI 工具，用于跟踪 UI 延迟、用户/句柄泄漏，以及通过实时 ETW 录制所有不平衡的资源分配，并实时显示泄漏/阻塞调用堆栈跟踪。
- `ETWController`：[^4] 一个录制工具，能够录制键盘输入和屏幕截图以及 ETW 数据。还支持同时在两台机器上进行分布式分析。由 Alois Kraus 开源。
- `UIForETW`：[^6] 一个围绕 xperf 的包装器，具有记录 Google Chrome 问题数据的特殊选项。还可以录制键盘和鼠标输入。由 Bruce Dawson 开源。

### 查看和分析 ETW 跟踪的工具

- `Windows Performance Analyzer` (WPA)：查看 ETW 数据最强大的 UI。WPA 可以可视化和叠加磁盘、CPU、GPU、网络、内存、进程等等更多的数据源，以便全面了解您的系统行为及其执行操作。虽然 UI 非常强大，但对于初学者来说也可能相当复杂。WPA 支持插件来处理来自其他来源的数据，而不仅仅是 ETW 跟踪。可以导入 Linux/Android[^8] 分析数据，这些数据是由 Linux perf、LTTNG、Perfetto 和以下日志文件格式生成的：dmesg、Cloud-Init、WaLinuxAgent、AndoidLogcat。
- `ETWAnalyzer`：[^5] 读取 ETW 数据并生成聚合摘要 JSON 文件，这些文件可以在命令行进行查询、过滤和排序，或者导出为 CSV 文件。
- `PerfView`：主要用于故障排除 .NET 应用程序。为垃圾回收和 JIT 编译触发的 ETW 事件被解析并作为报告或 CSV 数据轻松访问。

### 案例研究 - 程序启动缓慢 {.unlisted .unnumbered}

接下来，我们将通过一个示例，使用 ETWController 捕获 ETW 跟踪并使用 WPA 进行可视化。

**问题描述**: 在 Windows 资源管理器中双击下载的可执行文件时，它的启动会明显延迟。似乎有些东西延迟了进程启动。可能是什么原因？磁盘速度慢？

#### 设置

- 下载 ETWController 以录制 ETW 数据和屏幕截图。
- 下载最新的 Windows 11 Performance Toolkit[^1] 以便能够使用 WPA 查看数据。确保在系统环境对话框中将较新的 Win 11 `wpr.exe` 放置在您的路径之前，方法是将 WPT 的安装文件夹移动到 `C:\\Windows\\system32` 之前。它应该如下所示：
```
C> where wpr
C:\Program Files (x86)\Windows Kits\10\Windows Performance Toolkit\wpr.exe
C:\Windows\System32\wpr.exe
```

#### 捕获痕迹

- 启动 ETWController。
- 选择 CSwitch 配置文件以跟踪线程等待时间以及其他默认录制设置。保持复选框“*记录鼠标点击*”和“*获取循环屏幕截图*”启用，以便稍后借助屏幕截图导航到慢速点。参见图 @fig:ETWController_Dialog。
- 按“*开始录制*”。
- 从互联网下载一些可执行文件，解压缩它并双击可执行文件启动它。
- 之后，您可以通过按“*停止录制*”按钮停止分析。

![使用 ETWController UI 启动 ETW 收集.](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/perf-tools/ETWController_Dialog.png){#fig:ETWController_Dialog width=75%}

第一次停止分析需要更长的时间，因为所有托管代码都会生成合成 pdb，这是一个一次性操作。分析达到已停止状态后，您可以按“*在 WPA 中打开*”按钮，将 ETL 文件加载到 Windows Performance Analyzer 中，并附带 ETWController 提供的配置文件。CSwitch 配置文件会生成大量数据，这些数据存储在 4 GB 的环形缓冲区中，允许您在最旧的事件被覆盖之前录制 1-2 分钟。有时在正确的时间点停止分析有点艺术气息。如果您遇到偶发问题，可以将录制保持启用数小时，并在事件（例如文件中由轮询脚本检查的日志条目）出现时停止录制，以在问题发生时停止录制。

Windows 支持事件日志和性能计数器触发器，允许在性能计数器达到阈值或特定事件写入事件日志时启动脚本。如果您需要更复杂的停止触发器，应该看一下 PerfView，它允许定义一个性能计数器阈值，该阈值必须达到并在那里停留 x 秒，然后停止分析。这样，随机峰值就不会再触发误报。

#### 在 WPA 中分析

图 @fig:WPA_MainView 显示了在 Windows Performance Analyzer (WPA) 中打开的已录制 ETW 数据。WPA 视图分为三个部分：*CPU 使用率（采样）*、*通用事件* 和 *CPU 使用率（精确）*。为了理解它们之间的区别，让我们更深入地研究一下。上面 *CPU 使用率（采样）* 图表可用于识别 CPU 时间花在何处。数据是通过定期间隔对所有正在运行的线程进行采样收集的。与其他分析工具中的热点视图非常相似。

![Windows Performance Analyzer 应用程序启动缓慢概览.](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/perf-tools/WPA_MainView.png){#fig:WPA_MainView width=100% }

接下来是 *通用事件* 视图，其中显示鼠标点击和捕获的屏幕截图等事件。请记住，我们在 ETWController 窗口中启用了拦截这些事件的功能。因为事件放在时间线上，所以很容易将 UI 交互与系统如何响应它们相关联。

底部图表 *CPU 使用率（精确）* 使用的数据源与 *采样* 视图不同。虽然采样数据只会捕获正在运行的线程，但 *精确* 收集会考虑进程未运行的时间间隔。精确视图的数据来自 Windows 线程调度程序。它跟踪线程运行的时间和所处 CPU (CPU 使用率)、它在内核调用中被阻塞了多长时间 (等待)、它的优先级以及线程等待 CPU 可用有多长时间 (准备时间) 等。因此，精确视图不会显示顶级 CPU 耗用者。但是，这个视图对于理解某个进程被阻塞了多长时间以及 *为什么* 被阻塞非常有用。

现在我们熟悉了 WPA 界面，让我们观察一下图表。首先，我们可以在时间线上找到 `MouseButton` 事件 63 和 64。ETWController 将收集期间拍摄的所有屏幕截图保存在一个新建的文件夹中。分析数据本身保存在名为 `SlowProcessStart.etl` 的文件中，还有一个名为 `SlowProcessStart.etl.Screenshots` 的新文件夹。该文件夹包含屏幕截图和一个可以在浏览器中查看的 `Report.html` 文件。每个记录的键盘/鼠标交互都保存在一个以其事件编号命名的文件中，例如 `Screenshot_63.jpg`。图 @fig:ETWController_ClickScreenshot（已裁剪）显示鼠标双击（事件 63 和 64）。鼠标指针位置标记为绿色方块，除非单击事件发生，则为红色。这使得很容易发现何时何地执行了鼠标单击。

![使用 ETWController 捕获的鼠标点击屏幕截图.](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/perf-tools/ETWController_ClickScreenshot.png){#fig:ETWController_ClickScreenshot width=60% }

双击标志着我们应用程序等待某事时 1.2 秒延迟的开始。在时间戳 `35.1` 时，`explorer.exe` 处于活动状态，因为它试图启动新的应用程序。但后来它没有做太多工作，应用程序也没有启动。相反，`MsMpEng.exe` 接管执行直到时间 `35.7`。到目前为止，它看起来像是在下载的可执行文件允许启动之前进行防病毒扫描。但我们不能 100% 确定 `MsMpEng.exe` 正在阻止新应用程序的启动。

由于我们正在处理延迟，因此我们对 *CPU 使用率（精确）等待* 面板上可用的等待时间感兴趣。在那里，我们找到了我们的 `explorer.exe` 正在等待的进程列表，以条形图的形式可视化，与上部面板的时间线对齐。不难发现对应于 *Antivirus - Windows Defender* 的长条，其等待时间为 1.068 秒。因此，我们可以得出结论，启动我们应用程序的延迟是由 Defender 扫描活动引起的。如果您深入研究调用堆栈（未显示），您将看到系统调用 `CreateProcess` 在内核中被 `WDFilter.sys`（Windows Defender 筛选器驱动程序）延迟。它会阻止进程启动，直到扫描潜在恶意文件内容为止。防病毒软件可以拦截所有内容，从而导致难以诊断的性能问题，如果没有像 ETW 这样的全面内核视图。

谜题解开了吗？嗯，还不完全是。

知道 Defender 是问题只是第一步。如果您再看上面面板，您会看到延迟并不是完全由繁忙的防病毒扫描引起的。`MsMpEng.exe` 进程从时间 `35.1` 一直活跃到 `35.7`，但应用程序并没有立即启动之后。从时间 `35.7` 到 `36.2` 有额外的 0.5 秒延迟，在此期间 CPU 大部分处于空闲状态，什么都不做。要找到根本原因，需要跟踪跨进程的线程唤醒历史，我们将在此处不介绍。最后，您会发现一个阻止性的 Web 服务调用 `MpClient.dll!MpClient::CMpSpyNetContext::UpdateSpynetMetrics`，它确实等待某个 Microsoft Defender Web 服务做出响应。如果您还启用了 TCP/IP 或套接字 ETW 跟踪，您还可以找出 Microsoft Defender 与哪个远程端点通信。因此，延迟的第二部分是由 `MsMpEng.exe` 进程等待网络引起的，这也阻止了我们的应用程序运行。

这个案例研究只展示了一个使用 WPA 可以有效分析问题的例子，但还有其他类型的问​​题。WPA 界面非常丰富且高度可定制。它支持自定义配置文件，可以按照您喜欢的方式配置图表和表格以可视化 CPU、磁盘、文件等。最初，WPA 是为设备驱动程序开发人员开发的，并且内置了一些不专注于应用程序开发的配置文件。ETWController 带有自己的配置文件 (*Overview.wpaprofile*)，您可以将其设置为默认配置文件，位于 *配置文件 -> 保存启动配置文件* 下，以便始终使用性能概览配置文件。


[^1]: Windows SDK 下载 [https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/](https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/)
[^2]: Windows ADK 下载 [https://learn.microsoft.com/en-us/windows-hardware/get-started/adk-install#other-adk-downloads](https://learn.microsoft.com/en-us/windows-hardware/get-started/adk-install#other-adk-downloads)
[^3]: PerfView [https://github.com/microsoft/perfview](https://github.com/microsoft/perfview)
[^4]: ETWController [https://github.com/alois-xx/etwcontroller](https://github.com/alois-xx/etwcontroller)
[^5]: ETWAnalyzer [https://github.com/Siemens-Healthineers/ETWAnalyzer](https://github.com/Siemens-Healthineers/ETWAnalyzer)
[^6]: UIforETW [https://github.com/google/UIforETW](https://github.com/google/UIforETW)
[^7]: Performance HUD [https://www.microsoft.com/en-us/download/100813](https://www.microsoft.com/en-us/download/100813)
[^8]: Microsoft Performance Tools Linux / Android [https://github.com/microsoft/Microsoft-Performance-Tools-Linux-Android](https://github.com/microsoft/Microsoft-Performance-Tools-Linux-Android)

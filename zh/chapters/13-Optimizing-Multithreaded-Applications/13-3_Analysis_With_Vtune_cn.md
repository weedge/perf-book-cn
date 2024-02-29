## 使用 Intel VTune Profiler 进行分析

Intel VTune Profiler 有一种专门针对多线程应用程序的分析类型，称为[线程分析](https://software.intel.com/en-us/vtune-help-threading-analysis)。其摘要窗口（见图 @fig:MT_VtuneThreadSummary）显示了有关整个应用程序执行的统计信息，识别了我们在 [@sec:secMT_metrics] 中描述的所有指标。从有效 CPU 利用率直方图中，我们可以了解到有关捕获的应用程序行为的几个有趣事实。首先，平均而言，同时仅利用了 5 个硬件线程（图表中的逻辑核心）。其次，所有 8 个硬件线程同时活跃的情况非常罕见。

![来自[Phoronix 测试套件](https://www.phoronix-test-suite.com/)中 [x264](https://openbenchmarking.org/test/pts/x264) 基准测试的 Intel VTune Profiler 线程分析摘要。](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/mt-perf/VtuneThreadingSummary.png)<div id="MT_VtuneThreadSummary"></div>

### 查找开销大的锁

接下来，工作流程建议我们识别最有争议的同步对象。图 @fig:MT_VtuneThreadObjects 显示了这些对象的列表。我们可以看到 `__pthread_cond_wait` 显然突出，但由于程序中可能有几十个条件变量，我们需要知道哪一个是导致 CPU 利用率不佳的原因。

![显示了来自 [Phoronix 测试套件](https://www.phoronix-test-suite.com/)中 [x264](https://openbenchmarking.org/test/pts/x264) 基准测试的 Intel VTune Profiler 线程分析，显示了最有争议的同步对象。](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/mt-perf/VtuneThreadingWaitingObjects.png)<div id="MT_VtuneThreadObjects"></div>

要找出原因，我们可以简单地点击 `__pthread_cond_wait`，这将带我们到底部向上视图，如图 @fig:MT_VtuneLockCallStack 所示。我们可以看到导致线程等待条件变量的最频繁路径（等待时间的 47%）：`__pthread_cond_wait <- x264_8_frame_cond_wait <- mb_analyse_init`。

![显示了来自 [Phoronix 测试套件](https://www.phoronix-test-suite.com/)中 [x264](https://openbenchmarking.org/test/pts/x264) 基准测试的 Intel VTune Profiler 线程分析，显示了最有争议的条件变量的调用堆栈。](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/mt-perf/VtuneThreadingLockCallStack.png)<div id="MT_VtuneLockCallStack"></div>

接下来，我们可以通过双击分析中相应行来跳转到 `x264_8_frame_cond_wait` 函数的源代码视图，如图 @fig:MT_VtuneLockSourceCode 所示。接下来，我们可以研究锁的原因以及在这个地方使线程通信更有效的可能方法。[^15]

![显示了 [Phoronix 测试套件](https://www.phoronix-test-suite.com/)中 [x264](https://openbenchmarking.org/test/pts/x264) 基准测试中 `x264_8_frame_cond_wait` 函数的源代码视图。](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/mt-perf/VtuneThreadingLockSourceCode.png)<div id="MT_VtuneLockSourceCode"></div>

### 平台视图

Intel VTune Profiler 的另一个非常有用的功能是平台视图（见图 @fig:MT_VtunePlatform），它允许我们观察程序执行的任何给定时刻每个线程在做什么。这对于理解应用程序的行为并找到潜在的性能增长空间非常有帮助。例如，我们可以看到在从 1 秒到 3 秒的时间间隔内，只有两个线程在持续地利用相应 CPU 核心的约 100%（线程 ID 分别为 7675 和 7678）。在此期间，其他线程的 CPU 利用率是突发性的。

![显示了 [Phoronix 测试套件](https://www.phoronix-test-suite.com/)中 [x264](https://openbenchmarking.org/test/pts/x264) 基准测试的 Intel VTune Profiler 平台视图。](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/mt-perf/VtuneThreadingPlatformView.png)<div id="MT_VtunePlatform"></div>

平台视图还具有缩放和过滤功能。这使我们能够了解指定时间范围内每个线程在执行什么操作。要查看此内容，请在时间轴上选择范围，右键单击并选择“放大”和“按所选内容过滤”。Intel VTune Profiler 将显示在此时间范围内使用的函数或同步对象。

[^15]: 我不认为这将是一条容易的道路，并且不能保证您会找到使其更好的方法。
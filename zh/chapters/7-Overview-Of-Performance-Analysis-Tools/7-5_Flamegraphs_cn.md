## 火焰图

火焰图是一种流行的性能数据可视化方式，可以直观地呈现程序中最频繁的代码路径。它允许我们看到哪些函数调用占用了最大部分的执行时间。图 @fig:FlameGraph 展示了使用 Brendan Gregg 开发的开源脚本 [^1] 生成的 x264: [https://openbenchmarking.org/test/pts/x264](https://openbenchmarking.org/test/pts/x264) 视频编码基准测试的火焰图示例。如今，几乎所有性能分析器都可以在配置文件会话期间收集调用堆栈的情况下自动生成火焰图。

![A Flame Graph for [x264](https://openbenchmarking.org/test/pts/x264) benchmark.](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/perf-tools/Flamegraph.jpg)<div id="FlameGraph"></div>

在火焰图上，每个矩形（水平条）表示一个函数调用，矩形的宽度表示函数本身及其被调用者所花费的相对执行时间。函数调用是从下到上进行的，因此我们可以看到程序中最热的路径是 `x264 -> threadpool_thread_internal -> ... -> x264_8_macroblock_analyse`。函数 `threadpool_thread_internal` 及其被调用者占用了程序运行时间的 74%。但其自身时间，即函数本身花费的时间则相对较少。同样，我们可以对 `x264_8_macroblock_analyse` 进行相同的分析，它占用了 66% 的运行时间。这种可视化方式可以让您很好地直观地了解程序花费最多时间的地方。

火焰图是可交互的，您可以单击图像上的任何条形，它就会放大到特定的代码路径。您可以一直放大，直到找到与您的期望不符的地方，或者到达叶/尾函数——现在您就有了可以在分析中使用的可操作信息。另一种策略是找出程序中最热的函数（从这个火焰图中无法立即看出来），然后从下往上通过火焰图，试图理解这个最热的函数是从哪里被调用的。

[^1]: Brendan Gregg 的火焰图 - [https://github.com/brendangregg/FlameGraph](https://github.com/brendangregg/FlameGraph)

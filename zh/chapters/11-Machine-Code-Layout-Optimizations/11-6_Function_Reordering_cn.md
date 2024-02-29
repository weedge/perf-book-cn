## 函数重排序

根据前面各节描述的原则，可以将热点函数分组，进一步提高 CPU 前端缓存的利用率。当热点函数被分组在一起时，它们开始共享缓存行，这减少了*代码占用空间*，即 CPU 需要获取的缓存行总数。

图@fig:FunctionGrouping 给出了重新排列热点函数 `foo`、`bar` 和 `zoo` 的图形表示。图像上的箭头显示了最频繁的调用模式，即 `foo` 调用 `zoo`，然后 `zoo` 调用 `bar`。在默认布局中（见图@fig:FuncGroup_default），热点函数不相邻，它们之间有一些冷函数。因此，两个函数调用的序列（`foo` -> `zoo` -> `bar`）需要读取四个缓存行。

我们可以重新排列函数的顺序，使得热点函数彼此靠近（见图@fig:FuncGroup_better）。在改进的版本中，`foo`、`bar` 和 `zoo` 函数的代码适合于三个缓存行。另外，注意函数 `zoo` 现在根据函数调用的顺序被放置在 `foo` 和 `bar` 之间。当我们从 `foo` 调用 `zoo` 时，`zoo` 的开始已经在 I-cache 中。

<div id="fig:FunctionGrouping">

![默认布局](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/cpu_fe_opts/FunctionGrouping_Default.png)<div id="FuncGroup_default"></div>
![改进的布局](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/cpu_fe_opts/FunctionGrouping_Better.png)<div id="FuncGroup_better"></div>

重新排列热点函数。
</div>

与之前的优化类似，函数重排序提高了 I-cache 和 DSB-cache 的利用率。当存在许多小型热点函数时，这种优化效果最佳。

链接器负责将程序的所有函数布局在生成的二进制输出中。虽然开发人员可以尝试自己重新排列程序中的函数，但不能保证所需的物理布局。几十年来，人们一直使用链接器脚本来实现这个目标。如果你使用的是 GNU 链接器，这仍然是一种行之有效的方法。Gold 链接器 (`ld.gold`) 对这个问题有了更简单的解决方案。要在 Gold 链接器中获得二进制文件中函数的所需顺序，可以首先使用 `-ffunction-sections` 标志编译代码，这会将每个函数放入一个单独的节中。然后使用 [`--section-ordering-file=order.txt`](https://manpages.debian.org/unstable/binutils/x86_64-linux-gnu-ld.gold.1.en.html) 选项提供一个带有按所需最终布局排序的函数名称列表的文件。LLD 链接器也具有相同的特性，它是 LLVM 编译器基础设施的一部分，并通过 `--symbol-ordering-file` 选项访问。

解决将热点函数分组在一起的问题的一个有趣方法是由 Meta 的工程师在 2017 年引入的。他们实现了一个名为 [HFSort](https://github.com/facebook/hhvm/tree/master/hphp/tools/hfsort) 的工具[^1]，它根据分析数据自动生成节顺序文件 [[@HfSort](../References.md#HfSort)]。使用这个工具，他们观察到大型分布式云应用程序，如 Facebook、百度和维基百科的性能提高了 2\%。HFSort 已经集成到了 Meta 的 HHVM、LLVM BOLT 和 LLD 链接器中[^2]。从那时起，该算法首先被 HFSort+ 取代，最近又被 Cache-Directed Sort (CDSort[^3]) 所取代，对于具有大型代码占用空间的工作负载带来了更多改进。

[^1]: HFSort - [https://github.com/facebook/hhvm/tree/master/hphp/tools/hfsort](https://github.com/facebook/hhvm/tree/master/hphp/tools/hfsort)

[^2]: LLD 中的 HFSort - [https://github.com/llvm-project/lld/blob/master/ELF/CallGraphSort.cpp](https://github.com/llvm-project/lld/blob/master/ELF/CallGraphSort.cpp)

[^3]: LLVM 中的 Cache-Directed Sort - [https://github.com/llvm/llvm-project/blob/main/llvm/lib/Transforms/Utils/CodeLayout.cpp](https://github.com/llvm/llvm-project/blob/main/llvm/lib/Transforms/Utils/CodeLayout.cpp)
## 编译器优化报告 {#sec:compilerOptReports}

如今，软件开发在很大程度上依赖编译器进行性能优化。编译器在加速软件方面扮演着关键角色。大多数开发人员将优化代码的工作留给编译器，只有当他们发现编译器无法完成的优化机会时才会干预。可以说，这是一个好的默认策略。但是，当您追求最佳性能时，它就不太管用了。如果编译器没有执行关键优化，例如矢量化循环，怎么办？您将如何知道这一点？幸运的是，所有主流编译器都提供优化报告，我们现在将讨论这些报告。

假设您想知道一个关键循环是否被展开。如果是，展开因子是多少？有一种艰苦的方法可以知道这一点：研究生成的汇编指令。不幸的是，并不是每个人都习惯于阅读汇编语言。如果函数很大，它调用其他函数或也有许多被矢量化的循环，或者如果编译器为同一个循环创建了多个版本，这可能会特别困难。大多数编译器，包括 GCC、Clang 和 Intel 编译器（但不包括 MSVC），都提供优化报告，用于检查特定代码段执行了哪些优化。

让我们看一下 [@lst:optReport]，它展示了一个由 clang 16.0 未矢量化的循环示例。

代码清单：a.c {#lst:optReport}
```cpp
void foo(float* __restrict__ a, 
         float* __restrict__ b, 
         float* __restrict__ c,
         unsigned N) {
  for (unsigned i = 1; i < N; i++) {
    a[i] = c[i-1]; // value is carried over from previous iteration
    c[i] = b[i];
  }
}
```

在 clang 中生成优化报告，您需要使用 -Rpass*: https://llvm.org/docs/Vectorizers.html#diagnostics 标志：

```bash
$ clang -O3 -Rpass-analysis=.* -Rpass=.* -Rpass-missed=.* a.c -c
a.c:5:3: remark: loop not vectorized [-Rpass-missed=loop-vectorize]
  for (unsigned i = 1; i < N; i++) {
  ^
a.c:5:3: remark: unrolled loop by a factor of 8 with run-time trip count [-Rpass=loop-unroll]
  for (unsigned i = 1; i < N; i++) {
  ^
```

检查上面的优化报告，我们可以看到循环没有被矢量化，而是被展开了。开发人员并不总是很容易识别 [@lst:optReport] 第 6 行循环中是否存在循环进位依赖。由 c[i-1] 加载的值取决于前一次迭代的存储（参见图 @fig:VectorDep 中的操作 \circled{2} 和 \circled{3}）。可以通过手动展开循环的前几个迭代来揭示依赖关系：

```cpp
// iteration 1
  a[1] = c[0];
  c[1] = b[1]; // writing the value to c[1]
// iteration 2
  a[2] = c[1]; // reading the value of c[1]
  c[2] = b[2];
...
```

![Visualizing the order of operations in [@lst:optReport].](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/perf-analysis/VectorDep.png)<div id="VectorDep"></div>

如果我们将 [@lst:optReport] 中的代码矢量化，它会导致在数组 a 中写入错误的值。假设 CPU SIMD 单元可以一次处理四个浮点数，我们可以得到可以用以下伪代码表示的代码：
```cpp
// iteration 1
  a[1..4] = c[0..3]; // oops!, a[2..4] get wrong values
  c[1..4] = b[1..4]; 
...
```

[@lst:optReport] 中的代码无法矢量化，因为循环内部的操作顺序很重要。如 [@lst:optReport2] 所示，通过交换第 6 行和第 7 行可以修复此示例。这不会改变代码的语义，所以这是一个完全合法的更改。另外，可以通过将循环拆分成两个单独的循环来改善代码。

代码清单：a.c  {#lst:optReport2}
```cpp
void foo(float* __restrict__ a, 
         float* __restrict__ b, 
         float* __restrict__ c,
         unsigned N) {
  for (unsigned i = 1; i < N; i++) {
    c[i] = b[i];
    a[i] = c[i-1];
  }
}
```

在优化报告中，我们可以看到循环成功向量化了:

```bash
$ clang -O3 -Rpass-analysis=.* -Rpass=.* -Rpass-missed=.* a.c -c
a.cpp:5:3: remark: vectorized loop (vectorization width: 8, interleaved count: 4) [-Rpass=loop-vectorize]
  for (unsigned i = 1; i < N; i++) {
  ^
```

这只是使用优化报告的一个例子，我们将在本书的第二部分讨论发现矢量化机会时更详细地介绍。编译器优化报告可以帮助您找到错过的优化机会，并了解这些机会错过的原因。此外，编译器优化报告对于测试假设很有用。编译器通常会根据其成本模型分析来决定某个转换是否有益。但编译器并不总是做出最佳选择。一旦您在报告中发现缺少关键优化，您可以尝试通过更改源代码或向编译器提供提示（例如 `#pragma`、属性、编译器内置函数等）来纠正它。始终通过在实际环境中进行测量来验证您的假设。

编译器报告可能相当庞大，每个源代码文件都会生成单独的报告。有时，在输出文件中找到相关记录可能成为一项挑战。我们应该提到，最初这些报告的设计明确供编译器编写者用于改进优化过程。多年来，已经出现了一些工具，使它们更易于应用程序开发人员访问和操作。最值得注意的是 opt-viewer[^7] 和 optview2[^8]。此外，Compiler Explorer 网站还为基于 LLVM 的编译器提供了“优化输出”工具，当您将鼠标悬停在源代码相应行上时，它会报告执行的转换。所有这些工具都帮助可视化基于 LLVM 的编译器成功的和失败的代码转换。

在 LTO[^5] 模式下，一些优化是在链接阶段进行的。为了同时从编译和链接阶段发出编译器报告，应该向编译器和链接器传递专用选项。有关更多信息，请参见 LLVM "remarsk"[^6]指南。

Intel® [ISPC](https://ispc.github.io/ispc.html)[^3] 编译器 (已在 [@sec:ISPC] 中讨论) 采用稍微不同的方式报告缺失的优化。它会针对编译为相对低效代码的代码结构发出警告。无论哪种方式，编译器优化报告都应该是您工具箱中的关键工具之一。它是一种快速的方法，可以检查对特定热点进行了哪些优化，以及是否失败了一些重要的优化。许多改进机会都是通过编译器优化报告发现的。

[^1]: 使用编译器优化指令 - [https://easyperf.net/blog/2017/11/09/Multiversioning_by_trip_counts](https://easyperf.net/blog/2017/11/09/Multiversioning_by_trip_counts)
[^3]: ISPC - [https://ispc.github.io/ispc.html](https://ispc.github.io/ispc.html)
[^5]: 链接时间优化，也称为过程间优化(IPO)。阅读更多: [https://en.wikipedia.org/wiki/Interprocedural_optimization](https://en.wikipedia.org/wiki/Interprocedural_optimization)
[^6]: LLVM compiler remarks - [https://llvm.org/docs/Remarks.html](https://llvm.org/docs/Remarks.html)
[^7]: opt-viewer - [https://github.com/llvm/llvm-project/tree/main/llvm/tools/opt-viewer](https://github.com/llvm/llvm-project/tree/main/llvm/tools/opt-viewer)
[^8]: optview2 - [https://github.com/OfekShilon/optview2](https://github.com/OfekShilon/optview2)
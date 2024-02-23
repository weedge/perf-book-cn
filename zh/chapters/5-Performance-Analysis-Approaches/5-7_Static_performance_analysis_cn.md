## 静态性能分析

如今，我们拥有广泛的静态代码分析工具。对于 C 和 C++ 语言，我们有一些著名的工具，例如 Clang 静态分析器: [https://clang-analyzer.llvm.org/](https://clang-analyzer.llvm.org/)、Klocwork: [https://www.perforce.com/products/klocwork](https://www.perforce.com/products/klocwork)、Cppcheck: [http://cppcheck.sourceforge.net/](http://cppcheck.sourceforge.net/) 等。它们旨在检查代码的正确性和语义。同样，也有一些工具试图解决代码的性能方面的问题。静态性能分析器不会执行或分析程序，而是模拟代码，就好像它在真实硬件上执行一样。静态预测性能几乎是不可能的，因此这种类型的分析有很多限制。

首先，由于我们不知道要编译成的机器代码，所以不可能静态分析 C/C++ 代码的性能。因此，静态性能分析针对的是汇编代码。

其次，静态分析工具模拟工作负载而不是执行它。这显然非常慢，因此不可能静态分析整个程序。相反，工具会取一小段汇编代码，并试图预测它在真实硬件上的行为。用户应该选择特定的汇编指令（通常是小型循环）进行分析。因此，静态性能分析的范围非常窄。

静态性能分析器的输出相当低级，有时会将执行分解到 CPU 周期。通常，开发人员将其用于关键代码区域的细粒度调整，其中每个 CPU 周期都很重要。

### 静态分析器 vs. 动态分析器 {.unlisted .unnumbered}

**静态工具**: 不运行实际代码，而是尝试模拟执行，尽可能保留微架构细节。它们无法进行实际测量（执行时间、性能计数器），因为它们不运行代码。优点是您不需要拥有真正的硬件，可以针对不同代的 CPU 模拟代码。另一个好处是您不必担心结果的一致性：静态分析器总是会给您确定性的输出，因为模拟（与实际硬件上的执行相比）不会出现任何偏差。静态工具的缺点是它们通常无法预测和模拟现代 CPU 中的所有内容：它们基于一个可能存在错误和限制的模型。静态性能分析器的例子包括 UICA: [https://uica.uops.info/](https://uica.uops.info/)[^2] 和 llvm-mca: [https://llvm.org/docs/CommandGuide/llvm-mca.html](https://llvm.org/docs/CommandGuide/llvm-mca.html)[^3].

**动态工具**: 基于在真实硬件上运行代码并收集有关执行的所有信息。这是证明任何性能假设的唯一 100% 可靠的方法。缺点是，通常您需要具有特权访问权限才能收集低级性能数据，例如 PMCs。编写一个好的基准测试并测量您想要测量的内容并不总是容易的。最后，您需要过滤噪音和不同类型的副作用。动态微架构性能分析器的例子包括 nanoBench: [https://github.com/andreas-abel/nanoBench](https://github.com/andreas-abel/nanoBench),[^5] uarch-bench: [https://github.com/travisdowns/uarch-bench](https://github.com/travisdowns/uarch-bench)[^4] 等。

一个更大的静态和动态微架构性能分析工具集合可以在 这里: [https://github.com/MattPD/cpplinks/blob/master/performance.tools.md#microarchitecture](https://github.com/MattPD/cpplinks/blob/master/performance.tools.md#microarchitecture)[^7] 获得。

### 案例研究：使用 UICA 优化 FMA 吞吐量

开发人员经常会问的一个问题是：“最新处理器拥有 10 多个执行单元；我该如何编写代码让它们一直保持繁忙？” 这确实是一个最难解决的问题之一。有时它需要仔细观察程序如何运行。UICA 模拟器就是这样一个显微镜，可以让您深入了解您的代码如何流经现代处理器。

让我们看一下 [@lst:FMAthroughput] 中的代码。我们有意使示例尽可能简单。当然，现实世界中的代码通常比这更复杂。该代码将数组 `a` 的每个元素乘以常数 `B`，并将缩放后的值累积到 `sum` 中。在右侧，我们展示了使用 `-O3 -ffast-math -march=core-avx2` 编译时 Clang-16 生成的循环的机器代码。汇编代码看起来非常紧凑，让我们更好地理解它。

清单：FMA 吞吐量

~~~~ {#lst:FMAthroughput .cpp .numberLines}
float foo(float * a, float B, int N){  │ .loop:
  float sum = 0;                       │  vfmadd231ps ymm2, ymm1, ymmword [rdi + rsi]
  for (int i = 0; i < N; i++)          │  vfmadd231ps ymm3, ymm1, ymmword [rdi + rsi + 32]
    sum += a[i] * B;                   │  vfmadd231ps ymm4, ymm1, ymmword [rdi + rsi + 64]
  return sum;                          │  vfmadd231ps ymm5, ymm1, ymmword [rdi + rsi + 96]
}                                      │  sub rsi, -128
                                       │  cmp rdx, rsi
                                       │  jne .loop
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

这段代码是一个归约循环，即我们需要对所有乘积求和，最终返回一个浮点数。按照目前代码的写法，`sum` 上存在循环传递依赖性。您无法覆盖 `sum`，直到累积上一个乘积。一种并行化的巧妙方法是使用多个累加器并在最后将它们汇总。因此，我们可以用多个累加器代替单个 `sum`，例如 `sum1` 用于累积偶数次迭代的结果，`sum2` 用于累积奇数次迭代的结果。这就是 Clang-16 所做的：它使用了 4 个向量寄存器（`ymm2`-`ymm5`），每个都包含 8 个浮点累加器，并使用 FMA 将乘法和加法融合成单个指令。常量 `B` 被广播到 `ymm1` 寄存器中。`-ffast-math` 选项允许编译器重新关联浮点运算，我们将在 [@sec:Vectorization] 中讨论这个选项如何帮助优化。顺便说一句，乘法在循环后只需要做一次。这肯定是程序员的疏忽，但希望编译器将来能够处理它。

代码看起来不错，但它真的是最优的吗？让我们找出答案。我们将 [@lst:FMAthroughput] 中的汇编代码片段带到 UICA 进行模拟。在撰写本文时，UICA 不支持 Alderlake (英特尔第 12 代，基于 GoldenCove)，因此我们在最新可用的 RocketLake (英特尔第 11 代，基于 SunnyCove) 上运行了它。虽然架构不同，但这次实验暴露的问题在两者上都同样明显。模拟结果如图 @fig:FMA_tput_UICA 所示。这是一个类似于我们在第 3 章中展示的管道图。我们跳过了前两个迭代，只显示了第 2 和第 3 个迭代（最左列 "It."）。这时，执行已经达到稳定状态，所有后续迭代看起来都非常相似。

![UICA pipeline diagram. `I` = issued, `r` = ready for dispatch, `D` = dispatched, `E` = executed, `R` = retired.](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/perf-analysis/fma_tput_uica.png){#fig:FMA_tput_UICA width=100%}

UICA 是一个非常简化的实际 CPU 管道模型。例如，您可能会注意到指令提取和译码阶段丢失了。此外，UICA 不考虑缓存未命中和分支预测错误，因此它假设所有内存访问总是命中 L1 缓存并且分支总是预测正确。我们都知道这在现代处理器中并非如此。同样，这与我们的实验无关，因为我们仍然可以使用模拟结果来找到改进代码的方法。您能看到问题吗？

让我们仔细看看这个图表。首先，每个 FMA 指令都被分解成两个微操作 (见 \circled{1})：一个加载微操作，进入端口 `{2,3}`，一个 FMA 微操作，可以进入端口 `{0,1}`。加载微操作的延迟是 5 个周期：从第 11 个周期开始到第 15 个周期结束。FMA 微操作的延迟是 4 个周期：从第 19 个周期开始到第 22 个周期结束。所有 FMA 微操作都依赖于加载微操作，我们可以在图表上清楚地看到这一点：FMA 微操作总是对应加载微操作完成后才开始。现在找到第 10 个周期中的两个 `r` 单元格，它们已经准备调度，但是 RocketLake 只有两个加载端口，并且在同一个周期都被占用了。因此，这两个加载指令在下个周期发出。

该循环在 `ymm2-ymm5` 上具有四个跨迭代依赖性。来自指令 \circled{2} 的写入 `ymm2` 的 FMA 微操作无法在上一迭代的指令 \circled{1} 完成之前开始执行。请注意，来自指令 \circled{2} 的 FMA 微操作与指令 \circled{1} 完成执行的同一个周期 22 被调度。您也可以观察其他 FMA 指令的这种模式。

那么，您可能会问，“问题是什么？”。请看图片的右上角。对于每个周期，我们都计算了已执行的 FMA 微操作的数量，这不是 UICA 打印的。它看起来像 `1,2,1,0,1,2,1,...`，或者平均每个周期 1 个 FMA 微操作。最近的英特尔处理器大多有两个 FMA 执行单元，因此每个周期可以发出两个 FMA 微操作。该图表清楚地显示了差距，因为每个第四个周期都没有执行 FMA 指令。正如我们之前发现的，由于它们的输入 (`ymm2-ymm5`) 没有准备好，因此无法调度任何 FMA 微操作。

为了将 FMA 执行单元的利用率从 50% 提高到 100%，我们需要将循环展开两倍。这将使累加器的数量从 4 个增加到 8 个。此外，我们将有 8 个独立的数据流链，而不是 4 个。我们这里不会展示展开版本的模拟，您可以自己尝试。相反，让我们通过在真实硬件上运行两个版本来确认假设。顺便说一句，这是一个好主意，因为 UICA 等静态性能分析器并不是准确的模型。下面，我们展示了我们在最近的 Alderlake 处理器上运行的两个 nanobench: [https://github.com/andreas-abel/nanoBench](https://github.com/andreas-abel/nanoBench) 测试的输出。该工具采用提供的汇编指令 (`-asm` 选项) 并创建一个 benchmark 内核。读者可以查阅 nanobench 文档中其他参数的含义。左侧的原始代码在 4 个周期内执行 4 条指令，而改进后的版本可以在 4 个周期内执行 8 条指令。现在我们可以确定我们最大化了 FMA 执行吞吐量，右侧的代码使 FMA 单元始终处于忙碌状态。

```
# ran on Intel Core i7-1260P (Alderlake)
$ sudo ./kernel-nanoBench.sh -f -unroll 10   │ $ sudo ./kernel-nanoBench.sh -f -unroll 10 
 -loop 100 -basic -warm_up_count 10 -asm "   │  -loop 100 -basic -warm_up_count 10 -asm "
VFMADD231PS YMM0, YMM1, ymmword [R14];       │ VFMADD231PS YMM0, YMM1, ymmword [R14];
VFMADD231PS YMM2, YMM1, ymmword [R14+32];    │ VFMADD231PS YMM2, YMM1, ymmword [R14+32];
VFMADD231PS YMM3, YMM1, ymmword [R14+64];    │ VFMADD231PS YMM3, YMM1, ymmword [R14+64];
VFMADD231PS YMM4, YMM1, ymmword [R14+96];"   │ VFMADD231PS YMM4, YMM1, ymmword [R14+96];
-asm_init "<not shown>"                      │ VFMADD231PS YMM5, YMM1, ymmword [R14+128];
                                             │ VFMADD231PS YMM6, YMM1, ymmword [R14+160];
Instructions retired: 4.20                   │ VFMADD231PS YMM7, YMM1, ymmword [R14+192];
Core cycles: 4.02                            │ VFMADD231PS YMM8, YMM1, ymmword [R14+224]"
                                             │ -asm_init "<not shown>"
                                             │
                                             │ Instructions retired: 8.20
                                             │ Core cycles: 4.02
```

作为经验法则，在这种情况下，循环必须按 `T * L` 的倍数展开，其中 `T` 是指令的吞吐量，`L` 是其延迟。在我们的案例中，由于 Alderlake 上 FMA 的吞吐量为 2，延迟为 4 个周期，因此我们应该将其展开 `2 * 4 = 8` 倍以实现最大 FMA 端口利用率。这会创建 8 个可以独立执行的单独数据流链。

值得一提的是，在实践中您并不总是会看到 2 倍的加速。这只能在 UICA 或 nanobench 等理想化环境中实现。在实际应用程序中，即使您最大化了 FMA 的执行吞吐量，收益也可能会受到最终缓存未命中和其他流水线冲突的阻碍。发生这种情况时，缓存未命中的影响会超过 FMA 端口利用率不理想的影响。这很容易导致令人失望的 5% 速度提升。但别担心，你仍然做对了。

最后，让我们提醒您，UICA 或任何其他静态性能分析器都不适合分析大段代码。但它们非常适合探索微架构效应。此外，它们还可以帮助您建立 CPU 工作方式的心理模型。UICA 的另一个非常重要的用例是在循环中找到关键依赖性链，正如 easyperf 博客的 文章: [https://easyperf.net/blog/2022/05/11/Visualizing-Performance-Critical-Dependency-Chains](https://easyperf.net/blog/2022/05/11/Visualizing-Performance-Critical-Dependency-Chains)[^8] 中所述。

[^2]: UICA - [https://uica.uops.info/](https://uica.uops.info/)
[^3]: LLVM MCA - [https://llvm.org/docs/CommandGuide/llvm-mca.html](https://llvm.org/docs/CommandGuide/llvm-mca.html)
[^4]: uarch-bench - [https://github.com/travisdowns/uarch-bench](https://github.com/travisdowns/uarch-bench)
[^5]: nanoBench - [https://github.com/andreas-abel/nanoBench](https://github.com/andreas-abel/nanoBench)
[^7]: C++ 性能工具链接集合 - [https://github.com/MattPD/cpplinks/blob/master/performance.tools.md#microarchitecture](https://github.com/MattPD/cpplinks/blob/master/performance.tools.md#microarchitecture).
[^8]: Easyperf 博客 - [https://easyperf.net/blog/2022/05/11/Visualizing-Performance-Critical-Dependency-Chains](https://easyperf.net/blog/2022/05/11/Visualizing-Performance-Critical-Dependency-Chains)


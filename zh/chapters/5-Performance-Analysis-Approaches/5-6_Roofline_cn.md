## Roofline 性能模型 {#sec:roofline}

Roofline 性能模型是一个以吞吐量为导向的性能模型，在 HPC 领域广泛使用。它于 2009 年在加州大学伯克利分校开发。模型中的“roofline”表示应用程序的性能不能超过机器的能力。程序中的每个函数和每个循环都受到机器的计算或内存容量的限制。这个概念在图 @fig:RooflineIntro 中有所体现。应用程序的性能始终会受到某条“roofline”函数的限制。

![Roofline model. *© Image taken from [NERSC Documentation](https://docs.nersc.gov/development/performance-debugging-tools/roofline/#arithmetic-intensity-ai-and-achieved-performance-flops-for-application-characterization).*](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/perf-analysis/Roofline-intro.png){#fig:RooflineIntro width=80%}

硬件有两个主要限制：计算速度 (峰值计算性能，FLOPS) 和数据移动速度 (峰值内存带宽，GB/s)。应用程序的最大性能受峰值 FLOPS（水平线）和平台带宽乘以运算强度（对角线）两者之间的最小值限制。图 @fig:RooflineIntro 中的 roofline 图将两个应用程序 `A` 和 `B` 的性能与硬件限制进行了对比。应用程序 `A` 的运算强度较低，其性能受内存带宽限制，而应用程序 `B` 的计算密集型程度更高，因此不会受到内存瓶颈的太大影响。类似地，`A` 和 `B` 可以代表程序中的两个不同函数，并具有不同的性能特征。Roofline 性能模型会考虑到这一点，可以在同一个图表上显示应用程序的多个函数和循环。

算术强度 (AI) 是 FLOPS 和字节之间的比率，可以针对程序中的每个循环进行提取。让我们计算 [@lst:BasicMatMul] 中代码的算术强度。在最内层的循环体中，我们有一个加法和一个乘法；因此，我们有 2 个 FLOP。此外，我们还有三个读取操作和一个写入操作；因此，我们传输了 `4 ops * 4 bytes = 16` 个字节。该代码的算术强度为 `2 / 16 = 0.125`。AI 是给定性能点的 X 轴上的值。

代码清单：朴素并行矩阵乘法。 {#lst:BasicMatMul}
```cpp
void matmul(int N, float a[][2048], float b[][2048], float c[][2048]) {
    #pragma omp parallel for
    for(int i = 0; i < N; i++) {
        for(int j = 0; j < N; j++) {
            for(int k = 0; k < N; k++) {
                c[i][j] = c[i][j] + a[i][k] * b[k][j];
            }
        }
    }
}
```

传统的应用程序性能提升方式是充分利用机器的 SIMD 和多核能力。通常情况下，我们需要优化多个方面：矢量化、内存、线程。Roofline 方法可以帮助评估应用程序的这些特性。在 roofline 图表上，我们可以绘制标量单核、SIMD 单核和 SIMD 多核性能的理论最大值（见图 @fig:RooflineIntro2）。这将使我们了解改进应用程序性能的空间。如果我们发现我们的应用程序受计算绑定（即具有高算术强度）并且低于峰值标量单核性能，我们应该考虑强制矢量化（参见 [@sec:Vectorization]）并将工作分发到多个线程上。相反，如果应用程序的算术强度低，我们应该寻求改善内存访问的方法（参见 [@sec:MemBound]）。使用 Roofline 模型优化性能的最终目标是向上移动这些点。矢量化和线程化向上移动点，而通过增加算术强度优化内存访问则会将点向右移动，并且可能也会提高性能。

![Roofline model.](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/perf-analysis/Roofline-intro2.jpg){#fig:RooflineIntro2 width=70%}

理论最大值（roofline）通常在设备规范中给出，可以很容易地查阅。您也可以根据您使用的机器的特性计算理论最大值。一旦您知道机器的参数，这通常并不难做。对于 Intel Core i5-8259U 处理器，使用 AVX2 和 2 个 Fused Multiply Add (FMA) 单元的最大 FLOP 数（单精度浮点）可以计算如下：

$$
\begin{aligned}
\textrm{峰值 FLOPS} =& \textrm{ 8 (逻辑核心数量)}~\times~\frac{\textrm{256 (AVX 位宽)}}{\textrm{32 位 (float 大小)}} ~ \times ~ \\
& \textrm{ 2 (FMA)} \times ~ \textrm{3.8 GHz (最大睿频)} \\
& = \textrm{486.4 GFLOPs}
\end{aligned}
$$

我用于实验的 Intel NUC Kit NUC8i5BEH 的最大内存带宽可以如下计算。请记住，DDR 技术允许每次内存访问传输 64 位或 8 个字节。

$$
\begin{aligned}
\textrm{峰值内存带宽} = &~\textrm{2400 (DDR4 内存传输速率)}~\times~ \textrm{2 (内存通道)} ~ \times \\ &~ \textrm{8 (每次内存访问的字节数)} ~ \times \textrm{1 (插槽)}= \textrm{38.4 GiB/s}
\end{aligned}
$$

像 Empirical Roofline Tool: [https://bitbucket.org/berkeleylab/cs-roofline-toolkit/src/master/](https://bitbucket.org/berkeleylab/cs-roofline-toolkit/src/master/)[^2] 和 Intel Advisor: [https://software.intel.com/content/www/us/en/develop/tools/advisor.html](https://software.intel.com/content/www/us/en/develop/tools/advisor.html)[^3] 这样的自动化工具能够通过运行一组预先准备的基准测试来经验性地确定理论最大值。如果一个计算可以重用缓存中的数据，则可以实现更高的 FLOP 速度。Roofline 可以通过为每个内存层次引入专门的 roofline 来实现这一点（参见图 @fig:RooflineMatrix）。

确定硬件限制后，我们可以开始评估应用程序相对于 roofline 的性能。用于自动收集 Roofline 数据的两种最常用方法是采样（由 likwid: [https://github.com/RRZE-HPC/likwid](https://github.com/RRZE-HPC/likwid)[^4] 工具使用）和二进制插桩（由 Intel 软件开发仿真器 (SDE: [https://software.intel.com/content/www/us/en/develop/articles/intel-software-development-emulator.html](https://software.intel.com/content/www/us/en/develop/articles/intel-software-development-emulator.html)[^5] ) 使用）。采样在数据收集方面产生的开销较低，而二进制插桩则能提供更准确的结果。[^6] Intel Advisor 自动构建 Roofline 图表，并为给定循环的性能优化提供提示。图 @fig:RooflineMatrix 展示了 Intel Advisor 生成的 Roofline 图表示例。请注意，Roofline 图表使用的是对数刻度。

Roofline 方法可以通过在同一个图表上打印“之前”和“之后”的点来跟踪优化进度。因此，它是一个迭代的过程，指导开发人员帮助他们的应用程序充分利用硬件功能。图 @fig:RooflineMatrix 显示了对之前在 [@lst:BasicMatMul] 中显示的代码进行以下两个更改所带来的性能提升：

* 交换两个最内层的循环（交换第 4 和第 5 行）。这可以实现缓存友好的内存访问（参见 [@sec:MemBound]）。
* 使用 AVX2 指令启用最内层循环的自动矢量化。

![Roofline analysis for matrix multiplication on Intel NUC Kit NUC8i5BEH with 8GB RAM using clang 10 compiler.](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/perf-analysis/roofline_matrix.png){#fig:RooflineMatrix width=90%}

总结来说，Roofline 性能模型可以帮助：

* 识别性能瓶颈。
* 指导软件优化。
* 确定优化何时结束。
* 相对于机器能力评估性能。

**其他资源和链接**:

* NERSC 文档，网址： [https://docs.nersc.gov/development/performance-debugging-tools/roofline/](https://docs.nersc.gov/development/performance-debugging-tools/roofline/)。
* 劳伦斯伯克利国家实验室研究，网址： [https://crd.lbl.gov/departments/computer-science/par/research/roofline/](https://crd.lbl.gov/departments/computer-science/par/research/roofline/)
* 关于 Roofline 模型和 Intel Advisor 的视频演示集合，网址： [https://techdecoded.intel.io/](https://techdecoded.intel.io/) (搜索 "Roofline")。
* `Perfplot` 是一个脚本和工具集合，允许用户在最近的 Intel 平台上测量性能计数器，并使用结果生成 roofline 和性能图。网址： [https://github.com/GeorgOfenbeck/perfplot](https://github.com/GeorgOfenbeck/perfplot)

[^2]: Empirical Roofline Tool - [https://bitbucket.org/berkeleylab/cs-roofline-toolkit/src/master/](https://bitbucket.org/berkeleylab/cs-roofline-toolkit/src/master/).
[^3]: Intel Advisor - [https://software.intel.com/content/www/us/en/develop/tools/advisor.html](https://software.intel.com/content/www/us/en/develop/tools/advisor.html).
[^4]: Likwid - [https://github.com/RRZE-HPC/likwid](https://github.com/RRZE-HPC/likwid).
[^5]: Intel SDE - [https://software.intel.com/content/www/us/en/develop/articles/intel-software-development-emulator.html](https://software.intel.com/content/www/us/en/develop/articles/intel-software-development-emulator.html).
[^6]: 在此演示文稿中，可以看到更详细的收集 roofline 数据的方法比较：[https://crd.lbl.gov/assets/Uploads/ECP20-Roofline-4-cpu.pdf](https://crd.lbl.gov/assets/Uploads/ECP20-Roofline-4-cpu.pdf)



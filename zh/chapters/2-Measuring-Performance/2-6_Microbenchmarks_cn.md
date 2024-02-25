## 微基准测试

微基准测试是人们编写的小型独立程序，用于快速测试假设。通常，微基准测试用于选择某个相对较小算法或功能的最佳实现。几乎所有现代语言都有基准测试框架。在C++中，可以使用Google的[benchmark](https://github.com/google/benchmark)[^3]库，C#有[BenchmarkDotNet](https://github.com/dotnet/BenchmarkDotNet)[^4]库，Julia有[BenchmarkTools](https://github.com/JuliaCI/BenchmarkTools.jl)[^5]包，Java有[JMH](http://openjdk.java.net/projects/code-tools/jmh/etc)[^6]（Java Microbenchmark Harness）等等。

在编写微基准测试时，非常重要的一点是确保您要测试的场景在运行时确实被微基准测试执行。优化编译器可能会消除可能使实验无效的重要代码，甚至更糟的是，导致您得出错误的结论。在下面的示例中，现代编译器很可能会消除整个循环：

```cpp
// foo不会对字符串创建进行基准测试
void foo() {
  for (int i = 0; i < 1000; i++)
    std::string s("hi");
}
```

测试这一点的一种简单方法是检查基准测试的性能概要，并查看预期的代码是否突出显示为热点。有时可以立即发现异常的计时情况，因此在分析和比较基准测试运行时，请务必运用常识。防止编译器消除重要代码的一种流行方法是使用类似[`DoNotOptimize`](https://github.com/google/benchmark/blob/c078337494086f9372a46b4ed31a3ae7b3f1a6a2/include/benchmark/benchmark.h#L307)[^7]的辅助函数，其在底层执行必要的内联汇编操作：

```cpp
// foo对字符串创建进行基准测试
void foo() {
  for (int i = 0; i < 1000; i++) {
    std::string s("hi");
    DoNotOptimize(s);
  }
}
```

如果编写得当，微基准测试可以成为性能数据的良好来源。它们经常用于比较关键函数的不同实现的性能。一个好的基准测试的定义在于它是否在功能实际使用的真实条件下测试性能。如果基准测试使用与实践中给定的输入不同的合成输入，则该基准测试很可能会误导您，并导致您得出错误的结论。此外，当基准测试在没有其他要求的进程的系统上运行时，它具有所有可用的资源，包括DRAM和缓存空间。这样的基准测试可能会成为更快版本功能的冠军，即使它消耗的内存比其他版本多。但是，如果有占用DRAM的邻近进程，导致基准测试进程的内存区域被换出到磁盘，结果可能相反。

出于同样的原因，当从对函数进行单元测试中得出结果时，请谨慎。现代单元测试框架，例如GoogleTest，提供每个测试的持续时间。但是，这些信息不能替代一个精心编写的基准测试，该测试使用真实的输入在实际条件下测试函数（有关更多信息，请参见[[@fogOptimizeCpp](../References.md#fogOptimizeCpp)，第16.2章]）。在实践中无法复制确切的输入和环境，但这是开发人员在编写良好基准测试时应考虑的事项。

[^3]: Google benchmark库 - [https://github.com/google/benchmark](https://github.com/google/benchmark)
[^4]: BenchmarkDotNet - [https://github.com/dotnet/BenchmarkDotNet](https://github.com/dotnet/BenchmarkDotNet)
[^5]: Julia BenchmarkTools - [https://github.com/JuliaCI/BenchmarkTools.jl](https://github.com/JuliaCI/BenchmarkTools.jl)
[^6]: Java Microbenchmark Harness - [http://openjdk.java.net/projects/code-tools/jmh/etc](http://openjdk.java.net/projects/code-tools/jmh/etc)
[^7]: 对于JMH，这被称为`Blackhole.consume()`。
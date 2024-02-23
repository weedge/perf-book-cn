## SIMD 多处理器 {#sec:SIMD}

另一种被广泛用于许多工作负载的多处理器变体被称为单指令多数据（SIMD）。顾名思义，在SIMD处理器中，单个指令在单个周期内使用多个独立的功能单元操作许多数据元素。向量和矩阵的操作很适合SIMD架构，因为向量或矩阵的每个元素都可以使用相同的指令进行处理。SIMD架构可以更有效地处理大量数据，最适合涉及向量操作的数据并行应用程序。

图@fig:SIMD 展示了代码@lst:SIMD 中的标量和SIMD执行模式。在传统的SISD（单指令，单数据）模式中，加法操作分别应用于数组 `a` 和 `b` 的每个元素。然而，在SIMD模式中，加法同时应用于多个元素。如果我们针对具有能够对256位向量执行操作的执行单元的CPU架构进行优化，我们可以使用单个指令处理四个双精度元素。这导致发出的指令数量减少了4倍，并且可能比四个标量计算获得4倍的加速。但是在实践中，由于各种原因，性能优势并不那么直接。

代码清单：SIMD 执行 {#lst:SIMD .cpp}
```cpp
double *a, *b, *c;
for (int i = 0; i < N; ++i) {
  c[i] = a[i] + b[i];
}
```

![标量和SIMD操作的示例。](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/uarch/SIMD.png){#fig:SIMD width=80%}

对于常规的SISD指令，处理器使用通用寄存器。同样，对于SIMD指令，CPU有一组SIMD寄存器，用于保持从内存加载的数据和存储计算的中间结果。在我们的示例中，与数组 `a` 和 `b` 对应的两个连续的256位数据区域将从内存加载并存储在两个单独的向量寄存器中。接下来，将进行逐元素加法运算，并将结果存储在一个新的256位向量寄存器中。最后，将结果从向量寄存器写入对应于数组 `c` 的256位内存区域。请注意，数据元素可以是整数或浮点数。

大多数流行的CPU架构都具有矢量指令，包括x86、PowerPC、Arm和RISC-V。1996年，英特尔推出了MMX，一个针对多媒体应用程序设计的SIMD指令集。随后，英特尔引入了具有增强功能和增加矢量大小的新指令集：SSE、AVX、AVX2、AVX-512。Arm在其各个版本的架构中选择性地支持128位NEON指令集。在第8版（aarch64）中，这种支持变得是强制性的，并添加了新的指令。

随着新的指令集变得可用，开始着手使它们对软件工程师可用。利用SIMD指令所需的软件更改称为*代码向量化*。最初，SIMD指令是用汇编语言编程的。后来，引入了特殊的编译器内置函数，它们是一对一映射到SIMD指令的小函数。今天，所有主要的编译器都支持针对流行处理器的自动矢量化，即它们可以直接从C/C++、Java、Rust等高级语言编写的代码生成SIMD指令。

[TODO]:解释术语“循环余数”
[TODO]:或许解释/介绍掩码概念
[TODO]:解释术语“SIMD线(lane)”

为了使代码能够在支持不同矢量长度的系统上运行，Arm引入了SVE指令集。其定义特征是*可伸缩矢量*的概念：它们的长度在编译时是未知的。使用SVE，无需将软件移植到每种可能的矢量长度。用户不必重新编译其应用程序的源代码以利用在较新的CPU代中可用的更宽矢量。可伸缩矢量的另一个示例是RISC-V V扩展（RVV），该扩展于2021年底获得批准。一些实现支持相当宽（2048位）的矢量，并且最多可以将八个矢量组合在一起，形成`16,384`位的矢量，这极大地减少了执行的指令数量。在每次循环迭代中，用户代码通常执行 `ptr += number_of_lanes`，其中 `number_of_lanes` 在编译时是未知的。ARM SVE为这种长度相关操作提供了特殊指令，而RVV允许程序员查询/设置 `number_of_lanes`。

此外，CPU越来越多地加速机器学习中经常使用的矩阵乘法。英特尔的AMX扩展，支持Sapphire Rapids，将形状为16x64和64x16的8位矩阵相乘，并累积为32位的16x16矩阵。相比之下，苹果CPU中无关但同名的AMX扩展，以及ARM的SME扩展，计算存储在特殊的512位寄存器或可伸缩矢量中的一行和一列的外积。

最初，SIMD是由多媒体应用程序和科学计算推动的，但后来在许多其他领域找到了用途。随着时间的推移，SIMD指令集中支持的操作集稳步增加。除了图@fig:SIMD中显示的直接算术运算外，SIMD的新用途还包括：

- 字符串处理：查找字符，验证UTF-8，[1]解析JSON[^2]和CSV；[^3]
- 哈希运算，[^4]随机生成，[^5]密码学(AES)；
- 列式数据库（位打包、过滤、连接）；
- 对内置类型进行排序（VQSort，[^6]QuickSelect）；
- 机器学习和人工智能（加速PyTorch、Tensorflow）。

[^1]: UTF-8 验证 - [https://github.com/rusticstuff/simdutf8](https://github.com/rusticstuff/simdutf8)
[^2]: 解析 JSON - [https://github.com/simdjson/simdjson](https://github.com/simdjson/simdjson).
[^3]: 解析 CSV - [https://github.com/geofflangdale/simdcsv](https://github.com/geofflangdale/simdcsv)
[^4]: SIMD 哈希运算 - [https://github.com/google/highwayhash](https://github.com/google/highwayhash)
[^5]: 随机生成 - [Abseil 库](https://github.com/abseil/abseil-cpp/blob/master/absl/random/internal/randen.h)
[^6]: 排序 - [VQSort](https://github.com/google/highway/tree/master/hwy/contrib/sort)
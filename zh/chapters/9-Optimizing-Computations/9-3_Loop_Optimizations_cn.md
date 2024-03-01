## 循环优化

循环是几乎所有高性能程序的核心。由于循环代表了执行大量次的代码片段，因此它们是执行时间花费最多的部分。在这样一个关键代码段进行微小的更改可能会对程序的性能产生重大影响。这就是为什么仔细分析程序中热点循环的性能并了解改进它们的可能方法非常重要。

要有效地优化循环，关键是要了解性能瓶颈。一旦找到占用大部分时间的循环，就尝试确定限制其性能的因素。通常，它将是以下一种或多种情况：内存延迟、内存带宽或机器的计算能力。Roofline 性能模型（[@sec:roofline]）是评估不同循环相对于硬件理论最大值的性能的一个良好起点。自上而下的微架构分析（[@sec:TMA]）也可以成为有关瓶颈的另一个很好的信息来源。

在本节中，我们将研究针对上述瓶颈类型最著名的循环优化。我们首先讨论低级别的优化，这些优化只会在一个循环中移动代码。此类优化通常有助于提高循环内部计算的有效性。接下来，我们将研究重构循环的高级别优化，这些优化通常会影响多个循环。第二类优化通常旨在改进内存访问，消除内存带宽和内存延迟问题。请注意，这不是所有已知循环转换的完整列表。有关下面讨论的每个转换的更详细信息，读者可以参考 [[@EngineeringACompilerBook](../References.md#EngineeringACompilerBook)]。

编译器可以自动识别执行某些循环转换的机会。然而，有时需要开发人员干预才能达到所需的结果。在本节的第二部分，我们将分享一些有关如何发现循环优化机会的想法。了解对给定循环进行了哪些转换以及编译器未能进行哪些优化是成功性能调优的关键之一。最后，我们将考虑使用多面体框架优化循环的另一种方法。

### 低级优化

首先，我们将考虑一些简单的循环优化，这些优化会改变单个循环内的代码：循环不变代码移动（Loop Invariant Code Motion，LICM）、循环展开（Loop Unrolling）、循环强度降低（Loop Strength Reduction，LSR）和循环取消开关（Loop Unswitching）。这些优化通常有助于提高具有高算术强度循环的性能（见[@sec:roofline]），即当循环受CPU计算能力限制时。通常，编译器在执行这类转换方面做得很好；然而，仍然有一些情况可能需要开发者的支持。我们将在后续章节中讨论这些情况。

**循环不变代码移动（LICM）**：在循环中评估且从不改变的表达式称为循环不变量。由于它们的值在循环迭代中不会改变，我们可以将循环不变表达式移出循环。我们通过将结果存储在临时变量中，并在循环内部使用它来实现这一点（见[@lst:LICM](#LICM)）。现在所有不错的编译器在大多数情况下都能成功执行LICM。

代码清单：循环不变代码移动
<div id="LICM"></div>

```cpp
for (int i = 0; i < N; ++i)             for (int i = 0; i < N; ++i) {
  for (int j = 0; j < N; ++j)    =>       auto temp = c[i];
    a[j] = b[j] * c[i];                   for (int j = 0; j < N; ++j)
                                            a[j] = b[j] * temp;
                                        }
```

**循环展开**：循环中的累加变量是其值依赖于循环迭代次数的变量。例如，`v = f(i)`，其中`i`是迭代次数。在每次迭代中修改累加变量可能是不必要的且代价高昂。相反，我们可以展开循环，并为累加变量的每次增量执行多次迭代（见[@lst:Unrol](#Unrol)）。

代码清单：循环展开
<div id="Unrol"></div>

```cpp
for (int i = 0; i < N; ++i)             for (int i = 0; i+1 < N; i+=2) {
  a[i] = b[i] * c[i];          =>         a[i]   = b[i]   * c[i];
                                          a[i+1] = b[i+1] * c[i+1];
                                        }
```

循环展开的主要好处是每次迭代可以执行更多的计算。每次迭代结束时，索引值必须被增量、测试，并且如果还有更多迭代要处理，控制流会被分支回循环的顶部。这项工作可以被视为循环的“税”，可以减少。通过在[@lst:Unrol](#Unrol)中将循环展开2倍，我们将执行的比较和分支指令数量减少了一半。

循环展开是一种众所周知的优化；尽管如此，许多人对此感到困惑，并尝试手动展开循环。我建议没有开发者应该手动展开任何循环。首先，编译器在这方面做得很好，通常会非常优化地进行循环展开。第二个原因是，由于它们的乱序推测执行引擎（见[@sec:uarch]），处理器具有“嵌入式展开器”。当处理器等待第一次迭代中的长延迟指令完成时（例如加载、除法、微码指令、长依赖链），它会推测性地开始执行第二次迭代的指令，并且只等待循环携带的依赖项。这跨越了多个迭代，有效地在指令重排序缓冲区（ROB）中展开了循环。

**循环强度降低（LSR）**：用更便宜的指令替换昂贵的指令。这种转换可以应用于使用累加变量的所有表达式。强度降低通常应用于数组索引。编译器通过分析变量在循环迭代中的演变来执行LSR。在LLVM中，它被称为标量演化（Scalar Evolution，SCEV）。在[@lst:LSR](#LSR)中，编译器相对容易证明内存位置`b[i*10]`是循环迭代次数`i`的线性函数，因此它可以将昂贵的乘法替换为更便宜的加法。

代码清单：循环强度降低
<div id="LSR"></div>

```cpp
for (int i = 0; i < N; ++i)             int j = 0;
  a[i] = b[i * 10] * c[i];      =>      for (int i = 0; i < N; ++i) {
                                          a[i] = b[j] * c[i];
                                          j += 10;
                                        }
```

**循环取消开关（Loop Unswitching）**：如果循环内部有一个条件语句，并且它是不变的，我们可以将其移出循环。我们通过复制循环体，并将其版本放置在条件语句的每个`if`和`else`子句中来实现这一点（见[@lst:Unswitch](#Unswitch)）。虽然循环取消开关可能会使编写的代码量翻倍，但这些新循环现在可以分别进行优化。

代码清单：循环取消开关
<div id="Unswitch"></div>

```cpp
for (i = 0; i < N; i++) {               if (c)
  a[i] += b[i];                           for (i = 0; i < N; i++) {
  if (c)                       =>           a[i] += b[i];
    b[i] = 0;                               b[i] = 0;
}                                         }
                                        else
                                          for (i = 0; i < N; i++) {
                                            a[i] += b[i];
                                          }
```

### 高级优化

还有一类循环转换会改变循环的结构，通常会影响到多个嵌套循环。我们将探讨循环交换（Loop Interchange）、循环阻塞（Loop Blocking，也称为平铺或Tiling）、以及循环融合和分布（Loop Fusion and Distribution，也称为Fission）。这些转换的目的是改善内存访问，消除内存带宽和内存延迟的瓶颈。从编译器的角度来看，证明这类转换的合法性并证明它们的性能优势是非常困难的。在这个意义上，开发者处于一个更好的位置，因为他们只需要关心他们特定代码片段中转换的合法性，而不需要关心可能发生的每一种情况。不幸的是，这也意味着我们通常需要手动进行这样的转换。

**循环交换（Loop Interchange）**：交换嵌套循环的顺序的过程。内循环中使用的累加变量切换到外循环，反之亦然。[@lst:Interchange](#Interchange)展示了交换`i`和`j`嵌套循环的例子。循环交换的主要目的是对多维数组的元素进行顺序内存访问。通过遵循元素在内存中布局的顺序，我们可以提高内存访问的空间局部性，使我们的代码更加友好于缓存。这种转换有助于消除内存带宽和内存延迟的瓶颈。

代码清单：循环交换
<div id="Interchange"></div>

```cpp
for (i = 0; i < N; i++)                 for (j = 0; j < N; j++)
  for (j = 0; j < N; j++)          =>     for (i = 0; i < N; i++)
    a[j][i] += b[j][i] * c[j][i];           a[j][i] += b[j][i] * c[j][i];
```

循环交换仅在循环是*完全嵌套*的情况下才合法。完全嵌套的循环是指所有语句都在最内层循环中。交换不完全嵌套的循环嵌套更困难，但仍然可能，可以在[Codee](https://www.codee.com/catalog/glossary-perfect-loop-nesting/)[^1]目录中查看一个例子。

**循环阻塞（Loop Blocking，Tiling）**：这种转换的思想是将多维执行范围分割成更小的块（块或平铺），以便每个块都能适应CPU缓存。如果一个算法处理大型多维数组并对其元素进行跨步访问，那么缓存利用率很可能很低。每一次这样的访问可能会将未来访问请求的数据推出缓存（缓存驱逐）。通过将算法分割成更小的多维块，我们确保循环中使用的数据在被重用之前一直留在缓存中。

在[@lst:blocking](#blocking)所示的例子中，算法对数组`a`的元素进行行主序遍历，同时对数组`b`的元素进行列主序遍历。循环嵌套可以被分割成更小的块，以最大化数组`b`中元素的重用。

代码清单：循环阻塞
<div id="blocking"></div>

```cpp
// linear traversal                     // traverse in 8*8 blocks
for (int i = 0; i < N; i++)             for (int ii = 0; ii < N; ii+=8)
  for (int j = 0; j < N; j++)    =>      for (int jj = 0; jj < N; jj+=8)
    a[i][j] += b[j][i];                   for (int i = ii; i < ii+8; i++)
                                           for (int j = jj; j < jj+8; j++)
                                            a[i][j] += b[j][i];
```

循环阻塞是优化通用矩阵乘法（GEMM）算法的广泛已知方法。它增强了内存访问的缓存重用，并改善了算法的内存带宽和内存延迟。

通常，工程师会针对每个CPU核心的私有缓存大小（Intel和AMD的L1或L2，Apple的L1）来优化平铺算法。然而，私有缓存的大小随着代际变化而变化，因此硬编码块大小会带来一系列挑战。作为一种替代解决方案，可以使用[缓存无关](https://en.wikipedia.org/wiki/Cache-oblivious_algorithm)[^2]算法，其目标是在任何大小的缓存上都能合理地工作。

**循环融合和分布（Loop Fusion and Distribution，Fission）**：当它们迭代相同的范围且不引用彼此的数据时，可以合并分开的循环。一个循环融合的例子在[@lst:fusion](#fusion)中展示。相反的过程称为循环分布（Fission），即将循环分割成单独的循环。

代码清单：循环融合和分布
<div id="fusion"></div>

```cpp
for (int i = 0; i < N; i++)             for (int i = 0; i < N; i++) {
  a[i].x = b[i].x;                        a[i].x = b[i].x;
                               =>         a[i].y = b[i].y;
for (int i = 0; i < N; i++)             }
  a[i].y = b[i].y;                      
```

循环融合有助于减少循环开销（类似于循环展开），因为两个循环可以使用相同的累加变量。此外，循环融合还可以帮助提高内存访问的时间局部性。在[@lst:fusion](#fusion)中，如果结构体的`x`和`y`成员恰好位于同一缓存行上，那么融合两个循环会更好，因为我们可以避免两次加载相同的缓存行。这将减少缓存占用并提高内存带宽利用率。

然而，循环融合并不总是提高性能。有时，将循环分成多个阶段，预先过滤数据，排序和重新组织等会更好。通过将大循环分布成多个较小的循环，我们限制了每个循环迭代所需的数据量，有效地提高了内存访问的时间局部性。这在高缓存争用的情况下特别有帮助，这种情况通常发生在大循环中。循环分布还减少了寄存器压力，因为每个循环迭代中进行的操作更少。此外，将大循环分解成多个较小的循环可能对CPU前端的性能有益，因为指令缓存利用率更好。最后，当分布后，每个小循环可以由编译器进一步单独优化。

**循环展开和融合（Loop Unroll and Jam）**：要执行这种转换，首先需要展开外循环，然后将多个内循环融合在一起，如[@lst:unrolljam](#unrolljam)所示。这种转换增加了内循环的ILP（指令级并行性），因为内循环中执行了更多的独立指令。在代码示例中，内循环是一个归约操作，它累积数组`a`和`b`元素之间的差异。当我们以2的因子展开和融合循环嵌套时，我们实际上同时执行了初始外循环的2次迭代。这通过拥有2个独立的累加器来强调，这打破了初始变体中`diffs`的依赖链。

代码清单：循环展开和融合
<div id="unrolljam"></div>

```cpp
for (int i = 0; i < N; i++)           for (int i = 0; i+1 < N; i+=2)
  for (int j = 0; j < M; j++)           for (int j = 0; j < M; j++) {
    diffs += a[i][j] - b[i][j];   =>      diffs1 += a[i][j]   - b[i][j];
                                          diffs2 += a[i+1][j] - b[i+1][j];
                                        }
                                      diffs = diffs1 + diffs2;
```

循环展开和融合可以在没有跨迭代依赖的情况下执行外循环，换句话说，内循环的两次迭代可以并行执行。此外，如果内循环的内存访问在外部循环索引（本例中的`i`）上是跨步的，那么这种转换也是有意义的，否则其他转换可能更适用。当内循环的迭代次数较低时，例如小于4，展开和融合特别有用。通过进行转换，我们将更多的独立操作打包到内循环中，从而增加了ILP。

展开和融合转换有时对于外循环向量化非常有用，而在编写本文时，编译器无法自动执行。在内循环的迭代次数对编译器不可见的情况下，它仍然可以向量化原始内循环，希望它执行足够多的迭代以触发向量化代码（下一节将详细介绍向量化）。但如果迭代次数较低，程序将使用慢速的标量版本循环。一旦我们进行展开和融合，我们允许编译器以不同的方式向量化代码：现在将内循环中的独立指令“粘合”在一起（也称为SLP向量化）。

### 发现循环优化机会

正如我们在本节开头讨论的，编译器会承担优化循环的大部分工作。你可以依赖它们在循环代码中进行所有明显的改进，比如消除不必要的工作，执行各种窥孔优化等。有时，编译器足够聪明，可以默认生成循环的快速版本，而其他时候我们可能需要自己重写代码来帮助编译器。正如我们之前所说，从编译器的角度来看，合法且自动地执行循环转换是非常困难的。通常，当编译器无法证明转换的合法性时，它们必须保守处理。

考虑[@lst:Restrict](#Restrict)中的代码。编译器不能将表达式`strlen(a)`移出循环体。因此，循环在每次迭代时都会检查我们是否到达了字符串的末尾，这显然很慢。编译器不能提升调用的原因是，可能存在数组`a`和`b`的内存区域重叠的情况。在这种情况下，将`strlen(a)`移出循环体将是非法的。如果开发者确信内存区域不重叠，他们可以使用`restrict`关键字声明函数`foo`的两个参数，即`char* __restrict__ a`。

代码清单：不能将strlen移出循环
<div id="Restrict"></div>

```cpp
void foo(char* a, char* b) {
  for (int i = 0; i < strlen(a); ++i)
    b[i] = (a[i] == 'x') ? 'y' : 'n';
}
```

有时，编译器可以通过编译器优化备注（见[@sec:compilerOptReports]）告知我们转换失败。然而，在这种情况下，无论是Clang 10还是GCC 10都无法明确告诉我们表达式`strlen(a)`没有被提升出循环。找出这一点的唯一方法是根据应用程序的配置文件检查生成的汇编代码的热点部分。分析机器代码需要基本的汇编语言阅读能力，但这是一项非常有益的活动。

首先尝试获取容易实现的成果是一个合理的策略。开发者可以使用编译器优化报告或检查循环的机器代码来寻找简单的改进。有时，可以通过用户指令调整编译器转换。例如，当我们发现编译器将我们的循环展开4倍时，我们可以检查使用更高的展开因子是否会提高性能。大多数编译器支持`#pragma unroll(8)`，这将指示编译器使用用户指定的展开因子。还有其他控制特定转换的指令，如循环向量化、循环分布等。为了获取完整的用户指令列表，我们邀请用户查阅编译器手册。

接下来，开发者应该识别循环中的瓶颈，并根据硬件理论最大值评估性能。从Roofline Performance Model（[@sec:roofline]）开始，它将揭示开发者应该尝试解决的瓶颈。循环的性能受到以下一个或多个因素的限制：内存延迟、内存带宽或机器的计算能力。一旦识别出循环的瓶颈，开发者可以尝试应用本节前面讨论的某种转换。

尽管对于特定计算问题的优化技术众所周知，循环优化仍然是随着经验而来的“黑艺术”。我们建议你依赖编译器，并在必要时手动转换代码。最重要的是，尽可能保持代码简单，如果性能提升微不足道，不要引入不合理的复杂变化。

### 循环优化框架

多年来，研究人员已经开发了确定循环转换合法性的技术，并能够自动转换循环。其中一项发明就是[多面体框架](https://en.wikipedia.org/wiki/Loop_optimization#The_polyhedral_or_constraint-based_framework)[^3]。[GRAPHITE](https://gcc.gnu.org/wiki/Graphite)[^4] 是最早集成到生产编译器中的多面体工具之一。GRAPHITE基于从GCC的低级中间表示GIMPLE提取的多面体信息，执行一系列经典的循环优化。GRAPHITE证明了这种方法的可行性。

后来，LLVM编译器开发了自己的多面体框架，称为[Polly](https://polly.llvm.org/)[^5]。Polly是LLVM的一个高级循环和数据局部性优化基础设施。它使用基于整数多面体的抽象数学表示来分析和优化程序的内存访问模式。Polly执行经典的循环转换，特别是平铺和循环融合，以提高数据局部性。这个框架在许多知名基准测试上显示出显著的加速效果[@Grosser2012PollyP]。以下是一个示例，展示了Polly如何将[Polybench 2.0](https://web.cse.ohio-state.edu/~pouchet.2/software/polybench/)[^6] 基准测试套件中的通用矩阵乘法（GEMM）核心的执行速度提高近30倍：

```bash
$ clang -O3 gemm.c -o gemm.clang
$ time ./gemm.clang
real 0m6.574s
$ clang -O3 gemm.c -o gemm.polly -mllvm -polly
$ time ./gemm.polly
real 0m0.227s
```

Polly是一个强大的循环优化框架；然而，它仍然错过了一些常见且重要的情况。[^7] 它在LLVM基础设施的标准优化流程中未启用，需要用户提供明确的编译器选项来使用它（`-mllvm -polly`）。使用多面体框架是在寻找加速循环的方法时的一个可行选择。

[^1]: Codee: 完美循环嵌套 - [[https://www.codee.com/catalog/glossary-perfect-loop-nesting/](https://www.codee.com/catalog/glossary-perfect-loop-nesting/)]]([https://www.codee.com/catalog/glossary-perfect-loop-nesting/](https://www.codee.com/catalog/glossary-perfect-loop-nesting/))
[^2]: 缓存遗忘算法 - [https://en.wikipedia.org/wiki/Cache-oblivious_algorithm](https://en.wikipedia.org/wiki/Cache-oblivious_algorithm)
[^3]: 多面体框架 - [https://en.wikipedia.org/wiki/Loop_optimization#The_polyhedral_or_constraint-based_framework](https://en.wikipedia.org/wiki/Loop_optimization#The_polyhedral_or_constraint-based_framework).
[^4]: GRAPHITE 多面体框架 - [https://gcc.gnu.org/wiki/Graphite](https://gcc.gnu.org/wiki/Graphite).
[^5]: Polly - [https://polly.llvm.org/](https://polly.llvm.org/).
[^6]: Polybench - [https://web.cse.ohio-state.edu/~pouchet.2/software/polybench/](https://web.cse.ohio-state.edu/~pouchet.2/software/polybench/).
[^7]: Why not Polly? - [https://sites.google.com/site/parallelizationforllvm/why-not-polly](https://sites.google.com/site/parallelizationforllvm/why-not-polly).

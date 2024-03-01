 ## 基本块对齐

有时，性能会根据指令在内存中的偏移量而发生显着变化。考虑 [@lst:LoopAlignment](#LoopAlignment) 中提供的简单函数以及使用 `-O3 -march=core-avx2 -fno-unroll-loops` 编译时对应的机器码。为了说明这个想法，循环展开被禁用了。


代码清单:基本的块对齐 
<div id="LoopAlignment"></div>

```cpp
void benchmark_func(int* a) {    │ 00000000004046a0 <_Z14benchmark_funcPi>:
  for (int i = 0; i < 32; ++i)   │ 4046a0: mov rax,0xffffffffffffff80
    a[i] += 1;                   │ 4046a7: vpcmpeqd ymm0,ymm0,ymm0
}                                │ 4046ab: nop DWORD [rax+rax+0x0]
                                 │ 4046b0: vmovdqu ymm1,YMMWORD [rdi+rax+0x80] # loop begins
                                 │ 4046b9: vpsubd ymm1,ymm1,ymm0
                                 │ 4046bd: vmovdqu YMMWORD [rdi+rax+0x80],ymm1
                                 │ 4046c6: add rax,0x20
                                 │ 4046ca: jne 4046b0                          # loop ends
                                 │ 4046cc: vzeroupper 
                                 │ 4046cf: ret 
```

代码本身相当合理，但布局并不完美（见图 [@fig:Loop_default](#Loop_default)）。对应于循环的指令用黄色斜线突出显示。与数据缓存一样，指令缓存行长度为 64 字节。在图 [@fig:LoopLayout](#LoopLayout) 中，粗框表示缓存行边界。请注意，循环跨越多个缓存行：它从缓存行 `0x80-0xBF` 开始，并在缓存行 `0xC0-0xFF` 结束。为了获取在循环中执行的指令，处理器需要读取两个缓存行。这些情况通常会导致 CPU 前端的性能问题，尤其是对于上面呈现的小循环。

为了解决这个问题，我们可以使用 NOP 将循环指令向前移动 16 个字节，以便整个循环位于一个缓存行中。图 [@fig:Loop_better](#Loop_better) 显示了使用以蓝色突出显示的 NOP 指令执行此操作的效果。有趣的是，即使您在微基准测试中只运行这个热循环，性能影响也是可见的。这有点令人困惑，因为代码量很小，它不应该在任何现代 CPU 上占用 L1I 缓存的大小。图 [@fig:Loop_better](#Loop_better) 中布局性能更好的原因解释起来并不简单，并且会涉及大量微体系结构细节，我们在本书中不讨论这些细节。感兴趣的读者可以在 easyperf 博客上的文章 "Code alignment issues: [https://easyperf.net/blog/2018/01/18/Code_alignment_issues](https://easyperf.net/blog/2018/01/18/Code_alignment_issues)" 中找到更多信息。[^1]

<div id="LoopLayout">

![默认布局](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/cpu_fe_opts/LoopAlignment_Default.png)<div id="Loop_default"></div>

![改进布局](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/cpu_fe_opts/LoopAlignment_Better.png)<div id="Loop_better"></div>

[@lst:LoopAlignment](#LoopAlignment) 中循环的两种不同的代码布局。
</div>

默认情况下，LLVM 编译器会识别循环并将它们对齐到 16B 边界，如图 [@fig:Loop_default](#Loop_default) 所示。为了达到我们示例的所需代码位置，如图 [@fig:Loop_better](#Loop_better) 所示，可以使用 `-mllvm -align-all-blocks=5` 选项，该选项将在目标文件中将每个基本块对齐到 32 字节边界。但是，请谨慎使用此选项，因为它很容易在其他地方降低性能。此选项在执行路径上插入 NOP，这可能会增加程序的开销，尤其是当它们位于关键路径上时。NOP 不需要执行；但是，它们仍然需要从内存中获取、解码和退出。后者还会消耗 FE 数据结构和缓冲区中的空间用于簿记，类似于所有其他指令。LLVM 编译器中还有其他不那么侵入性的选项可用于控制基本块对齐，您可以在 easyperf 博客 post: [https://easyperf.net/blog/2018/01/25/Code_alignment_options_in_llvm](https://easyperf.net/blog/2018/01/25/Code_alignment_options_in_llvm) 中查看这些选项。[^6]

LLVM 编译器最近的新增功能是 `[[clang::code_align()]]` 循环属性，它允许开发人员在源代码中指定循环的对齐方式。这提供了对机器代码布局非常细粒度的控制。在引入此属性之前，开发人员不得不求助于一些不太实用的解决方案，例如在源代码中注入内联汇编语句 `asm(".align 64;")`。以下代码展示了如何使用新的 Clang 属性将循环对齐到 64 字节边界：

```c++
void benchmark_func(int* a) {
  [[clang::code_align(64)]]
  for (int i = 0; i < 32; ++i)
    a[i] += 1;
}
```

尽管 CPU 架构师努力将机器代码布局的影响最小化，但在某些情况下，代码放置（对齐）仍然会影响性能。机器代码布局也是性能测量的主要噪音源之一。它使区分真正的性能改进或回归与意外发生的回归（由代码布局的改变引起）变得更加困难。

[^1]: "Code alignment issues" - [https://easyperf.net/blog/2018/01/18/Code_alignment_issues](https://easyperf.net/blog/2018/01/18/Code_alignment_issues)
[^5]: x86 汇编指令手册 - [https://docs.oracle.com/cd/E26502_01/html/E28388/eoiyg.html](https://docs.oracle.com/cd/E26502_01/html/E28388/eoiyg.html)。此示例使用 MASM。否则，您会看到 `.align` 指令。
[^6]: "Code alignment options in llvm" - [https://easyperf.net/blog/2018/01/25/Code_alignment_options_in_llvm](https://easyperf.net/blog/2018/01/25/Code_alignment_options_in_llvm)

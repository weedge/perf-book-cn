## 使用配置分析文件引导的优化（Profile Guided Optimizations）{#sec:secPGO}

编译程序和生成最佳汇编代码都是关于启发式的。代码转换算法有很多特殊情况，旨在在特定情况下实现最佳性能。对于编译器做出的许多决策，它会尝试根据一些典型案例猜测最佳选择。例如，当决定是否内联特定函数时，编译器可能会考虑该函数被调用的次数。问题是编译器事先并不知道这一点。它首先需要运行程序才能找出答案。如果没有运行时信息，编译器就必须猜测。

这就是分析(profiling)信息派上用场的时候。有了分析(profiling)信息，编译器可以做出更好的优化决策。大多数编译器中有一组转换，可以根据反馈给他们的分析(profiling)数据调整算法。这组转换称为分析(profiling)优化 (PGO)。当分析(profiling)数据可用时，编译器可以用它来指导优化。否则，它将退回到使用其标准算法和启发式。有时在文献中，您可以找到术语反馈定向优化 (FDO)，它指的是与 PGO 相同的东西。

图 @fig:PGO_flow 显示了使用 PGO 的传统工作流程，也称为 *插桩化的(instrumented) PGO*。首先，您编译您的程序并告诉编译器自动检测代码。这将在函数中插入一些记账代码以收集运行时统计信息。第二个步骤是使用代表应用程序典型工作负载的输入数据运行插桩化的(instrumented)二进制文件。这将生成分析(profiling)数据，一个包含运行时统计信息的新文件。它是一个原始转储文件，其中包含有关函数调用计数、循环迭代计数和其他基本块命中计数的信息。此工作流程的最后一步是使用分析(profiling)数据重新编译程序以生成优化的可执行文件。

![使用工具 PGO 的工作流程.](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/cpu_fe_opts/pgo_flow.png){#fig:PGO_flow width=90% }

开发人员可以通过使用 `-fprofile-instr-generate` 选项构建程序来启用 LLVM 编译器中的 PGO 检测（步骤 1）。这将指示编译器检测代码，从而在运行时收集分析(profiling)信息。之后，LLVM 编译器可以使用 `-fprofile-instr-use` 选项使用分析(profiling)数据重新编译程序并输出经过 PGO 调整的二进制文件。clang 中使用 PGO 的指南在 文档: [https://clang.llvm.org/docs/UsersManual.html#profiling-with-instrumentation](https://clang.llvm.org/docs/UsersManual.html#profiling-with-instrumentation) 中进行了描述。[^7] GCC 编译器使用不同的选项集：`-fprofile-generate` 和 `-fprofile-use`，如 文档: [https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html#Optimize-Options](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html#Optimize-Options) 所述。[^10]

PGO 帮助编译器改进函数内联、代码放置、寄存器分配和其他代码转换。PGO 主要用于具有大型代码库的项目，例如 Linux 内核、编译器、数据库、网络浏览器、视频游戏、生产力工具等。对于拥有数百万行代码的应用程序，它是改善机器代码布局的唯一实践方法。使用分析(profiling)优化使生产工作负载的性能提高 10-25% 并不少见。

虽然许多软件项目将插桩化的(instrumented) PGO 作为其构建过程的一部分，但采用率仍然很低。这有几个原因。主要原因是插桩化的(instrumented)可执行文件的巨大运行时开销。运行插桩化的(instrumented)二进制文件和收集分析(profiling)数据经常会降低 5-10 倍的速度，这使构建步骤更长，并且阻止直接从生产系统（无论是在客户端设备还是云端）收集配置文件。不幸的是，您无法一次收集分析(profiling)数据并将其用于所有未来的构建。随着应用程序源代码的演变，配置文件数据会变得陈旧（不同步），需要重新收集。

PGO 流程的另一个注意事项是，编译器应该只使用应用程序将如何使用的代表性场景进行训练。否则，您最终可能会降低程序的性能。编译器会“盲目地”使用您提供的配置文件数据。它假设程序无论输入数据是什么都始终表现相同。PGO 的用户应该谨慎选择用于收集配置文件数据（步骤 2）的输入数据，因为在改进应用程序的一个用例的同时，其他用例可能会被悲观化。幸运的是，它不必仅仅是单个工作负载，因为来自不同工作负载的配置文件数据可以合并在一起，以代表应用程序的一组用例。

谷歌在 2016 年率先提出了另一种基于样本的 PGO 解决方案。[[@AutoFDO](../References.md#AutoFDO)] 除了检测代码之外，还可以从标准配置文件工具（例如 Linux `perf`）的输出中获取配置文件数据。谷歌开发了一个名为 AutoFDO: [https://github.com/google/autofdo](https://github.com/google/autofdo)[^8] 的开源工具，可以将 Linux `perf` 生成的采样数据转换为 GCC 和 LLVM 等编译器可以理解的格式。

与带仪器的 PGO 相比，这种方法有一些优点。首先，它消除了 PGO 构建工作流程的一个步骤，即步骤 1，因为无需构建带有仪器的二进制文件。其次，配置文件数据收集运行在已经优化的二进制文件上，因此运行时开销要低得多。这使得可以在生产环境中更长时间地收集配置文件数据。由于这种方法基于硬件收集，它还支持使用带仪器的 PGO 无法实现的新型优化。一个例子是分支到 cmov 转换，这是一个用条件移动替换条件跳转以避免分支预测错误开销的转换 (参见 [@sec:BranchlessPredication])。为了有效地执行此转换，编译器需要知道原始分支的错误预测频率。此信息可在现代 CPU（Intel Skylake+）上的基于样本的 PGO 中获得。

下一个创新想法来自 Meta，它在 2018 年年中开源了其名为 BOLT: [https://code.fb.com/data-infrastructure/accelerate-large-scale-applications-with-bolt/](https://code.fb.com/data-infrastructure/accelerate-large-scale-applications-with-bolt/) 的二进制优化工具。[^9] BOLT 在已经编译的二进制文件上工作。它首先反汇编代码，然后使用 Linux perf 等采样分析器收集的配置文件信息进行各种布局转换，然后重新链接二进制文件。[[@BOLT](../References.md#BOLT)] 截至今天，BOLT 拥有超过 15 个优化通道，包括基本块重新排序、函数拆分和重新排序等。与传统 PGO 类似，BOLT 优化的主要候选是遭受许多指令缓存和 iTLB 未命中折磨的程序。自 2022 年 1 月起，BOLT 成为 LLVM 项目的一部分，并作为独立工具提供。

谷歌在 BOLT 引入几年后开源了其名为 Propeller: [https://github.com/google/llvm-propeller/blob/plo-dev/Propeller_RFC.pdf](https://github.com/google/llvm-propeller/blob/plo-dev/Propeller_RFC.pdf) 的二进制重新链接工具。它具有类似的目的，但它不反汇编原始二进制文件，而是依赖于链接器输入，因此可以分布在多个机器上以实现更好的扩展和更少的内存消耗。BOLT 和 Propeller 等后链接优化器可以与传统 PGO (和 LTO) 结合使用，通常可以提供额外 5-10% 的性能提升。此类技术开辟了基于硬件遥测的新型二进制重写优化。

[^7]: Clang 中的 PGO - [https://clang.llvm.org/docs/UsersManual.html#profiling-with-instrumentation](https://clang.llvm.org/docs/UsersManual.html#profiling-with-instrumentation)
[^8]: AutoFDO - [https://github.com/google/autofdo](https://github.com/google/autofdo)
[^9]: BOLT - [https://code.fb.com/data-infrastructure/accelerate-large-scale-applications-with-bolt/](https://code.fb.com/data-infrastructure/accelerate-large-scale-applications-with-bolt/)
[^10]: GCC 中的 PGO - [https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html#Optimize-Options](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html#Optimize-Options)

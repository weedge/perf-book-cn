# {{ book.name }}

这是一本名为{{ book.en_name }}书籍的[源文件存储库](https://github.com/dendibakh/perf-book)的中文翻译，原版由 Denis Bakhvalov 等人编写。

- 原版电子书：https://book.easyperf.net/perf_book
- 中文翻译(第一版)：https://book.douban.com/subject/36243215/

**原作者第二版正在进行中！** 计划的更改在谷歌[文档](https://docs.google.com/document/d/1tr2qRDe72VSBYypIANYjJLM_zCdPB6S9m4LmXsQb0vQ/edit?usp=sharing)中进行了概述。计划中的新目录在 [new_toc.md](https://github.com/dendibakh/perf-book/blob/main/new_toc.md) 中。

**目的**：

  - 虽然已经有翻译的书籍;但是想follow更新,借助 『chatGPT』/『gemini/moonshot(kimi)』 翻译成中文，(加速学习节奏，掌握，并举一反三)
  - 英文源书是开源的，翻译成中文工作也持续更新，也是开源的，可以作为学习资料, 在线阅读可编辑，希望一起参与改进。
  - 对每章节的内容通过 『chatGPT』/『gemini/moonshot(kimi)』 进行归纳总结，结巩固知识点，并对课后练习进行回答,并验证答案。
  - 最后整体勘误，定搞。

> [!TIP]
> - 授之以鱼不如授之以渔, 使用AI赋能。
> - 性能优化分析数据可以借助『chatGPT』分析。
> - 『chatGPT』和『moonshot(kimi)』 翻译效果差不多(相同的prompt)，但是当问文中的规划练习和代码练习时，『moonshot(kimi)』不能理解问题，不过长文本上传根据章节翻译和归纳总结不错，毕竟不用翻墙就可以使用。

[@TODO]: 后续将上述流程用代码实现一个工作流(尽量)自动化翻译,归纳,Q&A的应用工具(CI)。

**在线阅读地址**: [https://weedge.github.io/perf-book-cn/zh/](https://weedge.github.io/perf-book-cn/zh/)

**中文版PDF(推荐)**: [https://raw.githubusercontent.com/weedge/perf-book-cn/main/perf-book-cn.pdf](https://raw.githubusercontent.com/weedge/perf-book-cn/main/perf-book-cn.pdf)

## 学习资料
1. https://github.com/dendibakh/perf-ninja
2. https://www.youtube.com/watch?v=2tzdkC6IDbo&list=PLRWO2AL1QAV6bJAU2kgB4xfodGID43Y5d
3. 现代cpu微架构(书中第一章微架构内容)：
   1. [Architecture All Access: Modern CPU Architecture Part 1 – Key Concepts | Intel Technology](https://www.youtube.com/watch?v=vgPFzblBh7w)
   2. [Architecture All Access: Modern CPU Architecture 2 - Microarchitecture Deep Dive ](https://www.youtube.com/watch?v=o_WXTRS2qTY) | [bilibili](https://www.bilibili.com/video/BV1a2421M7Tz/)


> [!TIP]
> - 文章中的`pandoc markdown`标签gitbook未能识别，暂未找到pandoc插件, 不影响整体阅读. (pandoc工具主要是用来生成离线PDF电子书, gitbook适合在线阅读)
> - [pandoc](https://pandoc.org/MANUAL.html) 通过bibtex生成引用样式: [citation-style-language(CSL)-styles](https://github.com/citation-style-language/styles), 可从 [Zotero Style 官网](https://www.zotero.org/styles) 挑选需要样式下载 
> - 翻译的[源文件存储库](https://github.com/dendibakh/perf-book)对应的commit: [5ddfadc](https://github.com/dendibakh/perf-book/commit/5ddfadc9c292b7dbac4d868e7a25b9a6ea3648c8)
> - 通过`pandoc`生成latex源文件，具体设置见：[https://github.com/weedge/perf-book/blob/feat/cn/export_book_zh.py](https://github.com/weedge/perf-book/blob/feat/cn/export_book_zh.py)

------

> [!NOTE] 
> 1. 在写代码时或多或少会知道一些代码层次(比如c++)的优化，但可能不知道为啥是这样的，这本书结合cpu讲解了相关原理(比如`unlikely`,`likely`)。
> 1. 木桶效应，通过监控测量分析，寻找性能短板在哪，结合场景对症下药(理解工作原理)
> 2. 了解现代cpu微体系架构(本文中提到的 Intel GoldenCove 架构白皮书[@IntelOptimizationManual](./chapters//References.md#IntelOptimizationManual)), 以小见大, 设计思路借鉴到业务系统中(虽然有些详细信息未公开)
> 3. AMD处理器 [@AMDProgrammingManual](./chapters/References.md#AMDProgrammingManual) ; ARM Neoverse V1处理器 [@ARMNeoverseV1](./chapters/References.md#ARMNeoverseV1)
> 4. 书中一些case介绍了优化工具的使用和性能分析
> 5. 阅读本书不需要详细了解每个性能分析工具的使用(比如常用的`perf`)，主要是针对cpu特性,memory的性能分析；只要记住有这个工具干啥用的，当遇到性能分析场景时，可以再次查阅该工具的使用方法即可；主要是结合工具去实践总结方法论。
> 6. 本书是针对现代CPU的性能分析和优化；前提条件是应用程序已经消除所有主要性能问题；如果想更深层次优化(比如底层存储系统, 流量请求最终汇聚点系统,核心系统等)，可以使用 CPU 性能监控功能来分析和进一步调整应用程序。仅当所有高级性能问题都已修复后，才建议使用硬件功能进行低级微调。在设计不良的算法系统上进行cpu分析调优只是时间上的浪费。
> 7. 底层硬件的持续性能分析(CP)在IaaS/PaaS云服务企业中常见。
> 8. 延伸阅读：[brendangregg-systems-performance](https://www.brendangregg.com/systems-performance-2nd-edition-book.html) | [brendangregg-bpf-performance](https://www.brendangregg.com/bpf-performance-tools-book.html) 必备性能分析工具书(函方法论实践)
> 9. 利用人工智能和 LLM 启发架构来处理性能分析样本，分析
> 函数之间关系，最终高精度地找出直接影响整体吞吐量和延迟的函数和库。[Raven.io](https://raven.io/)提供这种功能的一家公司
> 10. [源代码优化章节](./chapters/8-Optimizing-Memory-Accesses/8-0_Source_Code_Tuning_For_CPU_cn.md)重点掌握
    1. 编译链接层面静态分析，通过优化报告(比如: GCC的[`-fopt-info`](https://gcc.gnu.org/onlinedocs/gcc/Developer-Options.html#index-fopt-info);clang使用[`-Rpass*`](https://llvm.org/docs/Vectorizers.html#diagnostics))来获取优化建议(需要实践测试)
    2. **PGO** [基于性能分析引导的优化](./chapters/11-Machine-Code-Layout-Optimizations/11-7_PGO_cn.md) 练习: https://github.com/dendibakh/perf-ninja/blob/main/labs/misc/pgo/README.md (PGO 主要用于具有大型代码库的项目，比如：数据库，分布式文件系统); 特地场景，谨慎分析配置引导优化(可组合)。
> 11. 充分考虑到时间局部性和空间局部性对性能的影响
> 12. 尽量做扩展阅读，比如作者的博客文章，相关引用(比如：[@fogOptimizeCpp](./chapters/References.md#fogOptimizeCpp))
> 13. 对于cpu性能优化，有些已在编译器层面进行了优化，比如机器代码布局
> 14. 关注[低延迟系统的性能优化](./chapters/12-Other-Tuning-Areas/12-4_Low-Latency-Tuning-Techniques_cn.md) (比如HFT系统中的这个快速演讲：[CppCon 2018: Jonathan Keinan “Cache Warming: Warm Up The Code”](https://www.youtube.com/watch?v=XzRxikGgaHI); 这些关键路径代码值钱)
> 15. 优化多线程应用:
>     1. 借助可视化分析工具进行分析定位性能瓶颈(同步事件，锁，上下文切换)，书中举了一些case, Intel VTune Profiler 这个工具对于作者来说经常使用， 类似GPU性能分析工具 [nsight-compute](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html) (通过[nsight-systems](https://docs.nvidia.com/nsight-systems/UserGuide/index.html)分析系统整体性能耗时)；
>     2. 通过eBPF追踪内核中 futex 系统调用的执行（内核通过 futex 系统调用支持线程同步原语 - 互斥锁、信号量、条件变量等），从涉及的线程中收集有用的元数据
>     3. 尽量避免真共享下的数据竞争问题，通过编译器集成的 sanitizers 工具来识别，比如Clang [Thread sanitizer](https://clang.llvm.org/docs/ThreadSanitizer.html)
>     4. 避免伪共享。由于多核处理器cpu之间独立的L1/L2 cache，会出现cache line不一致的问题，为了解决这个问题，有相关协议模型，常用MESI协议，MESI 通过 这个网站模拟更直观的了解 https://www.scss.tcd.ie/Jeremy.Jones/VivioJS/caches/MESIHelp.htm ；为了保证一个core上修改的cache line数据同步到其他core的cache line上，则需要MESI协议来保证，如果同一个cache line上有个两个变量sum1 和 sum2 之间虽然没有相互依赖逻辑，但是当修改sum1 或者sum2 时，需要同步同一块cache line的内容，导致 即使没有相互关系的变量在同一cache line中， 需要彼此共享同步，从而出现所说的伪共享 flase sharing。伪共享因为cache line的同步会带来一些cpu 时钟周期的性能损失。
>     5. 深入了解并行编程： [Is Parallel Programming Hard, And, If So, What Can You Do About It?](https://mirrors.edge.kernel.org/pub/linux/kernel/people/paulmck/perfbook/perfbook.html)

----

> [!TIP] 
> 由于多核处理器cpu之间独立的L1/L2 cache，会出现cache line不一致的问题，为了解决这个问题，有相关协议模型，比如MESI协议来保证cache数据一致，同时由于CPU对「缓存一致性协议」进行的异步优化，对写和读分别引入了「store buffer」和「invalid queue」，很可能导致后面的指令查不到前面指令的执行结果（各个指令的执行顺序非代码执行顺序），这种现象很多时候被称作「CPU乱序执行」，为了解决乱序问题（也可以理解为可见性问题，修改完没有及时同步到其他的CPU），又引出了「内存屏障」的概念；内存屏障可以分为三种类型：写屏障，读屏障以及全能屏障（包含了读写屏障），屏障可以简单理解为：在操作数据的时候，往数据插入一条”特殊的指令”。只要遇到这条指令，那前面的操作都得「完成」。CPU当发现写屏障指令时，会把该指令「之前」存在于「store Buffer」所有写指令刷入高速缓存。就可以让CPU修改的数据马上暴露给其他CPU，达到「写操作」可见性的效果。读屏障也是类似的：CPU当发现读屏障的指令时，会把该指令「之前」存在于「invalid queue」所有的指令都处理掉。通过这种方式就可以确保当前CPU的缓存状态是准确的，达到「读操作」一定是读取最新的效果。由于不同CPU架构的缓存体系不一样、缓存一致性协议不一样、重排序的策略不一样、所提供的内存屏障指令也有差异，所以一些语言c++/java/go/rust 都有实现自己的内存模型, 比如 golang大牛Russ Cox写的内存模型系列文章 **Memory Models**: [https://research.swtch.com/mm](https://research.swtch.com/mm) 值得深入了解
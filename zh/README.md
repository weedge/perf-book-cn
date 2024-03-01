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
> - 『chatGPT』和『moonshot(kimi)』 翻译效果差不多(相同的prompt,调用openai接口知识蒸馏?)，但是当问文中的规划练习和代码练习时，『moonshot(kimi)』不能理解问题，不过长文本上传根据章节翻译和归纳总结不错，毕竟不用翻墙就可以使用。

[@TODO]: 后续将上述流程用代码实现一个工作流(尽量)自动化翻译,归纳,Q&A的应用工具(CI)。

**在线阅读地址**: [https://weedge.github.io/perf-book-cn/zh/](https://github.com/dendibakh/perf-ninja)

**中文版PDF(推荐)**: [https://raw.githubusercontent.com/weedge/perf-book-cn/main/perf-book-cn.pdf](https://raw.githubusercontent.com/weedge/perf-book-cn/main/perf-book-cn.pdf)

## 学习资料
1. https://github.com/dendibakh/perf-ninja
2. https://www.youtube.com/watch?v=2tzdkC6IDbo&list=PLRWO2AL1QAV6bJAU2kgB4xfodGID43Y5d


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
    2. **PGO** [@sec:secPGO] 练习: https://github.com/dendibakh/perf-ninja/blob/main/labs/misc/pgo/README.md (PGO 主要用于具有大型代码库的项目，比如：数据库，分布式文件系统); 特地场景，谨慎分析配置引导优化(可组合)。
> 11. 充分考虑到时间局部性和空间局部性对性能的影响
> 12. 尽量做扩展阅读，比如作者的博客文章，相关引用(比如：[@fogOptimizeCpp](./chapters/References.md#fogOptimizeCpp))
> 13. 对于cpu性能优化，有些已在编译器层面进行了优化，比如机器代码布局
> 14. 关注[低延迟系统的性能优化](./chapters/12-Other-Tuning-Areas/12-4_Low-Latency-Tuning-Techniques_cn.md) (比如HFT系统中的这个快速演讲：[CppCon 2018: Jonathan Keinan “Cache Warming: Warm Up The Code”](https://www.youtube.com/watch?v=XzRxikGgaHI); 这些关键路径代码值钱)

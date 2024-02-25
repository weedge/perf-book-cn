## 致谢 {.unlisted .unnumbered}

非常感谢Mark E. Dawson，他在撰写本书的几个部分时提供了帮助：《为DTLB优化》（[[sec:secDTLB](../8-Optimizing-Memory-Accesses/8-4_Reducing_DTLB_misses_cn.md#sec:secDTLB)]）、《为ITLB优化》（[@sec:FeTLB]）、《缓存预热》（[@sec:CacheWarm]）、系统调优（[@sec:SysTune]）、关于多线程应用程序性能扩展和开销的部分（[@sec:secAmdahl]）、使用COZ性能分析器的部分（[@sec:COZ]）、关于eBPF的部分（[@sec:secEBPF]）、《检测一致性问题》（[@sec:TrueFalseSharing]）。Mark是高频交易行业的知名专家。在撰写本书的不同阶段，Mark非常乐意分享他的专业知识和反馈意见。

接下来，我要感谢Sridhar Lakshmanamurthy，在关于CPU微体系结构的部分（[@sec:uarch]）中撰写了大部分内容。Sridhar在Intel工作了几十年，是半导体行业的老手。

非常感谢Nadav Rotem，他是LLVM编译器中矢量化框架的原始作者，他帮助我撰写了关于矢量化的部分（[@sec:Vectorization]）。

Clément Grégoire编写了关于ISPC编译器的部分（[@sec:ISPC]）。Clément在游戏开发行业拥有丰富的背景。他的评论和反馈帮助解决了游戏开发行业中一些挑战。

如果没有以下评论员的帮助，本书不可能从草稿中走出来：Dick Sites、Wojciech Muła、Thomas Dullien、Matt Fleming、Daniel Lemire、Ahmad Yasin、Michele Adduci、Clément Grégoire、Arun S. Kumar、Surya Narayanan、Alex Blewitt、Nadav Rotem、Alexander Yermolovich、Suchakrapani Datt Sharma、Renat Idrisov、Sean Heelan、Jumana Mundichipparakkal、Todd Lipcon、Rajiv Chauhan、Shay Morag 等等。

此外，我还要感谢整个性能社区为无数的博客文章和论文。我通过阅读Travis Downs、Daniel Lemire、Andi Kleen、Agner Fog、Bruce Dawson、Brendan Gregg等人的博客，学到了很多东西。我站在巨人的肩膀上，本书的成功不仅归功于我自己。本书是我向整个社区致敬和回馈的方式。

最后但并非最不重要的是，感谢我的家人，他们耐心地容忍我错过周末旅行和晚间散步。没有他们的支持，我不可能完成这本书。

\sectionbreak

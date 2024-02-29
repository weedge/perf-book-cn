## 缓存一致性问题 {#sec:TrueFalseSharing}

### 缓存一致性协议

多处理器系统采用缓存一致性协议来确保每个包含独立缓存的独立内核共享使用内存时的数据一致性。如果没有这样的协议，如果CPU A和CPU B都将内存位置L读取到各自的缓存中，然后处理器B随后修改其缓存值L，那么CPU将具有相同内存位置L的不一致值。缓存一致性协议确保对缓存条目的任何更新都忠实地更新在同一位置的任何其他缓存条目中。

MESI（**M**odified **E**xclusive **S**hared **I**nvalid）是最著名的缓存一致性协议之一，用于支持现代 CPU 中使用的回写缓存。其缩写表示缓存行可以标记的四种状态（参见图 @fig:MESI）：

* **修改（Modified）：** 缓存行仅存在于当前缓存中，并且已从其在 RAM 中的值进行修改
* **独占（Exclusive）：** 缓存行仅存在于当前缓存中，并且与其在 RAM 中的值匹配
* **共享（Shared）：** 缓存行存在于这里和其他缓存行中，并且与其在 RAM 中的值匹配
* **无效（Invalid）：** 缓存行未使用（即不包含任何 RAM 位置）

![MESI 状态图. *© Image by University of Washington via courses.cs.washington.edu.*](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/mt-perf/MESI_Cache_Diagram.jpg)<div id="MESI"></div>


从内存中获取时，每个缓存行都将一个状态编码到其标签中。然后，缓存行状态会从一个状态转换到另一个状态。[^25] 现实中，CPU 供应商通常会实现稍作改进的 MESI 变体。例如，英特尔使用 MESIF: [https://en.wikipedia.org/wiki/MESIF_protocol](https://en.wikipedia.org/wiki/MESIF_protocol)，[^26] 它添加了转发 (F) 状态，而 AMD 则使用 MOESI: [https://en.wikipedia.org/wiki/MOESI_protocol](https://en.wikipedia.org/wiki/MOESI_protocol)，[^27] 它添加了拥有 (O) 状态。但这些协议仍然保持了基本 MESI 协议的本质。

正如早期示例所示，缓存一致性问题会导致程序出现顺序不一致的问题。这个问题可以通过使用窥探缓存来监视所有内存事务并相互协作以保持内存一致性来缓解。不幸的是，这也伴随着成本，因为一个处理器的修改会使另一个处理器缓存中的对应缓存行失效。这会导致内存停顿并浪费系统带宽。与只能为应用程序性能设置上限的序列化和锁定问题不同，一致性问题会导致由 USL 在 [@sec:secAmdahl] 中描述的逆行效应。两种广为人知的缓存一致性问题是“真共享”和“假共享”，我们将在下面进一步探讨。

### 真共享 {#sec:secTrueSharing}

真共享指的是两个不同的处理器访问同一个变量（请参见 [@lst:TrueSharing]）。

代码清单:真正的共享示例。 {#lst:TrueSharing}
```cpp
unsigned int sum;
{ // parallel section
  for (int i = 0; i < N; i++)
    sum += a[i]; // sum is shared between all threads
}
```

真实共享意味着存在数据竞争，这很难被检测到。幸运的是，有一些工具可以帮助识别这类问题。Clang 的 Thread sanitizer: [https://clang.llvm.org/docs/ThreadSanitizer.html](https://clang.llvm.org/docs/ThreadSanitizer.html)[^30] 和 helgrind: [https://www.valgrind.org/docs/manual/hg-manual.html](https://www.valgrind.org/docs/manual/hg-manual.html)[^31] 就是其中的一些工具。为了防止 [@lst:TrueSharing] 中的数据竞争，应该将 `sum` 变量声明为 `std::atomic<unsigned int> sum`。

当发生真实共享时，使用 C++ 原子类型可以帮助解决数据竞争问题。然而，它实际上序列化了对原子变量的访问，这可能会降低性能。解决真实共享问题的另一种方法是使用线程局部存储 (TLS)。TLS 是一种方法，允许给定多线程进程中的每个线程分配内存来存储线程特定的数据。通过这样做，线程修改自己的本地副本，而不是争用全局可用的内存位置。可以使用 TLS 类说明符 (`thread_local unsigned int sum`，自 C++11 起) 声明 `sum` 来修复 [@lst:TrueSharing] 中的示例。然后，主线程应该合并每个工作线程所有本地副本的结果。

## 假共享 {#sec:secFalseSharing}

假共享[^29] 发生在两个不同的处理器修改位于同一缓存行上的不同变量时（参见 [@lst:FalseSharing]）。图 @fig:FalseSharing 展示了假共享问题。

代码清单: 假共享示例。 {#lst:FalseSharing}
```
struct S {
  int sumA; // sumA and sumB are likely to
  int sumB; // reside in the same cache line
};
S s;

{ // section executed by thread A
  for (int i = 0; i < N; i++)
    s.sumA += a[i];
}

{ // section executed by thread B
  for (int i = 0; i < N; i++)
    s.sumB += b[i];
}
```

![False共享:两个线程访问同一个缓存行。 *© Image by Intel Developer Zone via software.intel.com.*](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/mt-perf/FalseSharing.jpg)<div id="FalseSharing"></div>

假共享是多线程应用程序性能问题的常见来源。因此，现代分析工具内置了检测此类案例的支持。TMA 将经历真/假共享的应用程序描述为内存绑定。通常，在这种情况下，您会看到 争用访问: [https://software.intel.com/en-us/vtune-help-contested-accesses](https://software.intel.com/en-us/vtune-help-contested-accesses)[^18] 指标的高值。

使用 Intel VTune Profiler 时，用户需要两种类型的分析来查找和消除假共享问题。首先，运行 微架构探索: [https://software.intel.com/en-us/vtune-help-general-exploration-analysis](https://software.intel.com/en-us/vtune-help-general-exploration-analysis)[^19] 分析，该分析实施 TMA 方法来检测应用程序中是否存在假共享。正如之前提到的，争用访问指标的高值促使我们深入挖掘并运行启用了“分析动态内存对象”选项的 内存访问: [https://software.intel.com/en-us/vtune-help-memory-access-analysis](https://software.intel.com/en-us/vtune-help-memory-access-analysis) 分析。此分析有助于找出导致争用问题的对数据结构的访问。通常，这些内存访问具有高延迟，分析会揭示这一点。有关使用 Intel VTune Profiler 修复假共享问题的示例，请参见 英特尔开发者社区: [https://software.intel.com/en-us/vtune-cookbook-false-sharing](https://software.intel.com/en-us/vtune-cookbook-false-sharing)[^20]。

Linux `perf` 也支持查找假共享。与 Intel VTune Profiler 一样，首先运行 TMA（请参见 [@sec:secTMA_Intel]）以找出程序是否经历假/真共享问题。如果是这种情况，请使用 `perf c2c` 工具检测具有高缓存一致性成本的内存访问。`perf c2c` 匹配不同线程的存储/加载地址，并查看是否命中了修改后的缓存行。读者可以在专门的 博客文章: [https://joemario.github.io/blog/2016/09/01/c2c-blog/](https://joemario.github.io/blog/2016/09/01/c2c-blog/)[^21] 中找到该过程及其如何使用工具的详细解释。

可以通过对齐/填充内存对象来消除假共享。[@sec:secTrueSharing] 中的示例可以通过确保 `sumA` 和 `sumB` 不共享同一缓存行来修复（请参阅 [@sec:secMemAlign] 中的详细信息）。

从一般的性能角度来看，最重要的考虑因素是可能状态转换的成本。在所有缓存状态中，唯一不涉及昂贵的跨缓存子系统通信和 CPU 读/写操作期间的数据传输的是修改 (M) 和独占 (E) 状态。因此，缓存行保持“M”或“E”状态的时间越长（即跨缓存的数据共享越少），多线程应用程序产生的一致性成本就越低。有关如何利用此属性的示例，请参见 Nitsan Wakart 的博客文章“深入了解缓存一致性: [http://psy-lob-saw.blogspot.com/2013/09/diving-deeper-into-cache-coherency.html](http://psy-lob-saw.blogspot.com/2013/09/diving-deeper-into-cache-coherency.html)"[^28]。

[^18]: 争用访问 - [https://software.intel.com/en-us/vtune-help-contested-accesses](https://software.intel.com/en-us/vtune-help-contested-accesses).
[^19]: Vtune 一般探索分析 - [https://software.intel.com/en-us/vtune-help-general-exploration-analysis](https://software.intel.com/en-us/vtune-help-general-exploration-analysis).
[^20]: Vtune 食谱：假共享 - [https://software.intel.com/en-us/vtune-cookbook-false-sharing](https://software.intel.com/en-us/vtune-cookbook-false-sharing).
[^21]: 关于 `perf c2c` 的文章 - [https://joemario.github.io/blog/2016/09/01/c2c-blog/](https://joemario.github.io/blog/2016/09/01/c2c-blog/).
[^25]: 读者可以在此处观看和测试动画 MESI 协议：
[https://www.scss.tcd.ie/Jeremy.Jones/vivio/caches/MESI.htm](https://www.scss.tcd.ie/Jeremy.Jones/vivio/caches/MESI.htm).
[^26]: MESIF - [https://en.wikipedia.org/wiki/MESIF_protocol](https://en.wikipedia.org/wiki/MESIF_protocol)
[^27]: MOESI - [https://en.wikipedia.org/wiki/MOESI_protocol](https://en.wikipedia.org/wiki/MOESI_protocol)
[^28]: 博客文章“深入缓存一致性”- [http://psy-lob-saw.blogspot.com/2013/09/diving-deeper-into-cache-coherency.html](http://psy-lob-saw.blogspot.com/2013/09/diving-deeper-into-cache-coherency.html)
[^29]: 值得注意的是，错误共享不仅在C/C++/Ada等低级语言中可以观察到，在Java/C#等高级语言中也可以观察到。
[^30]: Clang的线程消毒工具:[https://clang.llvm.org/docs/ThreadSanitizer.html](https://clang.llvm.org/docs/ThreadSanitizer.html)。
[^31]: Helgrind，一个线程错误检测工具:[https://www.valgrind.org/docs/manual/hg-manual.html](https://www.valgrind.org/docs/manual/hg-manual.html)。
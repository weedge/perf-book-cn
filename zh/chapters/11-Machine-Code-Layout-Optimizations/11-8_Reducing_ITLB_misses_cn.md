## 减少 ITLB 未命中 {#sec:FeTLB}

调整前端效率的另一个重要领域是内存地址的虚拟到物理地址转换。这些转换主要由 TLB（参见 [@sec:TLBs]）提供服务，TLB 在专用条目中缓存最近使用的内存页转换。当 TLB 无法处理翻译请求时，将进行耗时的内核页表页面遍历，为每个引用的虚拟地址计算正确的物理地址。每当您在 TMA 摘要中看到高比例的 ITLB 开销时，本节中的建议可能派上用场。

通常情况下，相对较小的应用程序不易受到 ITLB 未命中的影响。例如，Golden Cove 微架构可以在其 ITLB 中覆盖高达 1MB 的内存空间。如果您的应用程序的机器代码适合 1MB，您应该不会受到 ITLB 未命中的影响。当应用程序中频繁执行的部分分散在内存周围时，问题就开始出现。当许多函数开始频繁相互调用时，它们会开始争夺 ITLB 中的条目。一个例子是 Clang 编译器，在撰写本文时，它的代码部分大约为 60MB。在运行主流 Intel CoffeeLake 处理器的笔记本电脑上，ITLB 开销约为 7%，这意味着 7% 的周期被浪费在处理 ITLB 未命中上：执行要求苛刻的页面遍历和填充 TLB 条目。

另一组经常受益于使用大页的大内存应用程序包括关系数据库（例如 MySQL、PostgreSQL、Oracle）、托管运行时（例如 Javascript V8、Java JVM）、云服务（例如网络搜索）、网络工具（例如 node.js）。将代码段映射到大页可以将 ITLB 未命中数量减少高达 50% [[@IntelBlueprint](../References.md#IntelBlueprint)]，从而为某些应用程序带来高达 10% 的加速。但是，与许多其他功能一样，大页并不适用于所有应用程序。可执行文件只有几 KB 大的小程序最好使用常规 4KB 页面而不是 2MB 大页；这样，内存可以更有效地利用。

减少 ITLB 压力的总体思路是将应用程序性能关键代码的部分映射到 2MB（大页）上。但通常情况下，整个应用程序的代码部分会重新映射以简化操作，或者如果您不知道哪些函数是热门函数。要进行这种转换，关键要求是代码部分与 2MB 边界对齐。在 Linux 上，这可以通过两种不同的方式实现：使用附加链接器选项重新链接二进制文件或在运行时重新映射代码部分。这两个选项都展示在 easyperf.net 博客[^1] 上。据我们所知，它在 Windows 上是不可能的，因此我们只展示如何在 Linux 上进行操作。

第一个选项可以通过使用 `-Wl,-zcommon-page-size=2097152 -Wl,-zmax-page-size=2097152` 选项链接二进制文件来实现。这些选项指示链接器将代码段放在 2MB 边界，以便启动时由加载器将其放置在 2MB 页面上。这种放置的缺点是链接器将被迫插入多达 2MB 的填充（浪费）字节，使二进制文件更加臃肿。以 Clang 编译器为例，它使二进制文件的大小从 111MB 增加到 114MB。重新链接二进制文件后，我们在 ELF 二进制头中设置一个特殊位，该位确定文本段是否应默认由大页支持。最简单的方法是使用 libhugetlbfs: [https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO](https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO)[^12] 软件包中的 `hugeedit` 或 `hugectl` 工具。例如：

```bash
# 永久设置 ELF 二进制头中的特殊位。
$ hugeedit --text /path/to/clang++
# 代码段将默认使用大页加载。
$ /path/to/clang++ a.cpp

# 在运行时覆盖默认行为。
$ hugectl --text /path/to/clang++ a.cpp
```

第二个选项是在运行时重新映射代码段。此选项不需要代码段与 2MB 边界对齐，因此可以在不重新编译应用程序的情况下工作。这种方法背后的 idea 是在程序启动时分配大页并将所有代码段转移到那里。该方法的参考实现是在 iodlr: [https://github.com/intel/iodlr](https://github.com/intel/iodlr)[^2] 中实现的。一个选项是从您的 `main` 函数调用该功能。另一个更简单的方法是构建动态库并在命令行中预加载它：

```bash
$ LD_PRELOAD=/usr/lib64/liblppreload.so clang++ a.cpp
```
虽然第一种方法只能使用显式大页，但使用 `iodlr` 的第二种方法既适用于显式大页，也适用于透明大页。有关如何在 Windows 和 Linux 上启用大页的说明，请参见附录 C。

除了采用大页之外，还可以使用优化 I-cache 性能的标准技术来改善 ITLB 性能。例如，重新排序函数以更好地定位热门函数，通过链接时优化 (LTO/IPO) 减少热门区域的大小，使用概要引导优化 (PGO) 和 BOLT，以及减少激进内联。

BOLT 提供了 `-hugify` 选项，可以根据配置文件数据自动将大页用于热门代码。使用此选项时，`llvm-bolt` 将注入代码，在运行时将热门代码放在 2MB 页面上。该实现利用了 Linux 透明大页 (THP)。这种方法的优点是只有少部分代码映射到大页，所需的大页数量最小化，因此页面碎片减少。

[^1]: "使用大页为代码带来的性能优势" - [https://easyperf.net/blog/2022/09/01/Utilizing-Huge-Pages-For-Code](https://easyperf.net/blog/2022/09/01/Utilizing-Huge-Pages-For-Code).
[^2]: iodlr 库 - [https://github.com/intel/iodlr](https://github.com/intel/iodlr).
[^12]: libhugetlbfs - [https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO](https://github.com/libhugetlbfs/libhugetlbfs/blob/master/HOWTO).

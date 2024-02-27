## 缓存友好数据结构

编写缓存友好的算法和数据结构是打造高性能应用程序的重要因素之一。缓存友好代码的关键支柱是我们之前在 [@sec:MemHierar] 描述的局部性原理，包括时间局部性和空间局部性。这里的目标是允许高效地从缓存中获取所需数据。在设计缓存友好代码时，考虑缓存行而不只是单个变量及其在内存中的位置会很有帮助。

### 顺序访问数据

利用缓存空间局部性的最佳方式是进行顺序内存访问。通过这样做，我们可以让硬件预取器（参见 [@sec:HwPrefetch]）识别内存访问模式并提前引入下一块数据。[@lst:CacheFriend] 中展示了 C 代码示例，它执行了此类缓存友好访问。该代码之所以“缓存友好”，是因为它按照矩阵在内存中的布局顺序访问矩阵元素（行优先遍历: [https://en.wikipedia.org/wiki/Row-_and_column-major_order](https://en.wikipedia.org/wiki/Row-_and_column-major_order)[^6]）。交换数组中索引的顺序（即 `matrix[column][row]`）将导致以列为主的矩阵遍历，这不会利用空间局部性并会损害性能。

代码清单:缓存友好的内存访问。 {#lst:CacheFriend .cpp}
```cpp
for (row = 0; row < NUMROWS; row++)
  for (column = 0; column < NUMCOLUMNS; column++)
    matrix[row][column] = row + column;
```

[@lst:CacheFriend] 中展示的例子是一个经典例子，但现实世界中的应用程序通常要复杂得多。有时您需要付出更多努力才能编写缓存友好的代码。例如，在已排序的大数组中进行二分搜索的标准实现并没有利用空间局部性，因为它测试的是彼此相距甚远、不共享同一缓存行的不同位置的元素。解决这个问题最著名的方式是使用 Eytzinger 布局存储数组元素[[@EytzingerArray](../References.md#EytzingerArray)]。它的想法是使用类似 BFS 的布局（通常在二进制堆中看到）将一个隐式的二叉搜索树打包到数组中。如果代码在数组中执行大量二分搜索，将其转换为 Eytzinger 布局可能会有益处。

### 使用合适的容器

几乎任何语言都提供各种现成的容器。但了解它们的底层存储和性能影响很重要。[[@fogOptimizeCpp](../References.md#fogOptimizeCpp), Chapter 9.7 Data structures, and container classes] 提供了一个很好的关于选择合适的 C++ 容器的逐步指南。

此外，选择数据存储时要考虑代码将如何使用它。考虑一种情况，需要在数组中存储对象与存储指向这些对象的指针之间进行选择，而对象的大小较大。指针数组占用更少的内存。这将使修改数组的操作受益，因为指针数组需要更少的内存传输。然而，当保留对象本身时，通过数组进行线性扫描会更快，因为它更符合缓存，不需要间接内存访问。[^8]

### 数据压缩

通过使数据更紧凑可以改善内存层次结构的利用率。有许多方法可以压缩数据。经典示例之一是使用位字段。[@lst:PackingData1] 展示了在数据打包时代码可能获益的例子。如果我们知道 `a`, `b` 和 `c` 代表需要一定数量位才能编码的枚举值，我们就可以减少结构体 `S` 的存储空间（参见 [@lst:PackingData2]）。

代码清单:打包数据:基线结构体。 {#lst:PackingData1 .cpp}
```cpp
struct S {
  unsigned a;
  unsigned b;
  unsigned c;
}; // S is `sizeof(unsigned int) * 3` bytes
```

代码清单:打包数据:打包的结构体。 {#lst:PackingData2 .cpp}
```cpp
struct S {
  unsigned a:4;
  unsigned b:2;
  unsigned c:2;
}; // S is only 1 byte
```

这大大减少了来回传输的内存量并节省了缓存空间。请记住，这会带来访问每个打包元素的成本。由于 `b` 的位与 `a` 和 `c` 共享同一个机器字，编译器需要执行 `>>` (右移) 和 `&` (AND) 操作来加载它。类似地，需要 `<<` (左移) 和 `|` (OR) 操作将值存储回去。在额外计算比低效内存传输引起的延迟更便宜的地方，数据打包是有益的。

此外，当避免编译器添加的填充（参见 [@lst:PackingData3] 中的示例）时，程序员可以通过重新排列结构或类中的字段来减少内存使用。编译器插入未使用的内存字节（填充）的原因是为了允许高效地存储和获取结构的单个成员。在该示例中，如果将 `S1` 的成员按其大小递减的顺序声明，则可以减小其大小。

代码清单:避免编译填充。 {#lst:PackingData3 .cpp}
```cpp
struct S1 {
  bool b;
  int i;
  short s;
}; // S1 is `sizeof(int) * 3` bytes

struct S2 {
  int i;
  short s;  
  bool b;
}; // S2 is `sizeof(int) * 2` bytes
```

### 对齐和填充 {#sec:secMemAlign}

改善内存子系统利用率的另一个技术是对齐数据。可能出现这种情况，即一个大小为 16 字节的对象占用两个缓存行，即它从一个缓存行开始并结束于下一个缓存行。获取这样一个对象需要两个缓存行读取，如果对象正确对齐，可以避免这种情况。[@lst:AligningData] 展示了如何使用 C++11 的 `alignas` 关键字对齐内存对象。

代码清单:使用"alignas"关键字对齐数据。 {#lst:AligningData .cpp}
```cpp
// Make an aligned array
alignas(16) int16_t a[N];

// Objects of struct S are aligned at cache line boundaries
#define CACHELINE_ALIGN alignas(64) 
struct CACHELINE_ALIGN S {
  //...
};
```

如果变量存储在可被其自身大小整除的内存地址上，则访问它的效率最高。例如，一个 double 类型变量占用 8 个字节的存储空间，因此最好将其存储在一个可被 8 整除的地址上。这个大小通常是 2 的幂次方。大于 16 个字节的对象应该存储在一个可被 16 整除的地址上。[[@fogOptimizeCpp](../References.md#fogOptimizeCpp)]

对齐可能会导致未使用字节的空洞，从而降低内存带宽利用率。在上面的例子中，如果结构体 `S` 只有 40 个字节，那么下一个 `S` 对象将会从下一个缓存行的开头开始，这会在每个保存 `S` 结构体的缓存行中留下 64 - 40 = 24 个未使用的字节。

有时需要填充数据结构成员以避免一些极端情况，例如缓存争用 [[@fogOptimizeCpp](../References.md#fogOptimizeCpp), 第 9.10 章 缓存争用] 和伪共享 (参见 [@sec:secFalseSharing])。例如，在多线程应用程序中，当两个线程 A 和 B 访问同一结构的不同字段时，可能会出现伪共享问题。[@lst:PadFalseSharing1] 展示了可能发生这种情况的代码示例。由于结构体 `S` 的成员 `a` 和 `b` 可能占据同一个缓存行，因此缓存一致性问题可能会显著减慢程序运行速度。为了解决这个问题，可以填充 `S` 使得成员 `a` 和 `b` 不共享同一个缓存行，如 [@lst:PadFalseSharing2] 所示。

代码清单:填充数据:基线版本。 {#lst:PadFalseSharing1 .cpp}
```cpp
struct S {
  int a; // written by thread A
  int b; // written by thread B
};
```

代码清单:填充数据:改进版本。 {#lst:PadFalseSharing2 .cpp}
```cpp
#define CACHELINE_ALIGN alignas(64) 
struct S {
  int a; // written by thread A
  CACHELINE_ALIGN int b; // written by thread B
};
```

使用 `malloc` 进行动态分配时，保证返回的内存地址满足目标平台的最小对齐要求。一些应用程序可能受益于更严格的对齐。例如，以 64 字节对齐而不是默认的 16 字节对齐动态分配 16 字节。POSIX 系统的用户可以利用 `memalign`: [https://linux.die.net/man/3/memalign](https://linux.die.net/man/3/memalign)[^13] API 来实现这一目的。其他人可以像 这里: [https://embeddedartistry.com/blog/2017/02/22/generating-aligned-memory/](https://embeddedartistry.com/blog/2017/02/22/generating-aligned-memory/)[^14] 所描述的那样自己实现。

对齐考虑最重要的领域之一是 SIMD 代码。当依赖于编译器自动矢量化时，开发人员无需做任何特殊操作。但是，当您使用编译器向量内联函数编写代码时 (参见 [@sec:secIntrinsics])，它们通常要求地址可被 16、32 或 64 整除。编译器内联头文件中提供的向量类型已经做了注释，以确保适当的对齐。[[@fogOptimizeCpp](../References.md#fogOptimizeCpp)]

```cpp
// ptr will be aligned by alignof(__m512) if using C++17
__m512 * ptr = new __m512[N];
```
### 动态内存分配

首先，有很多可以替代 `malloc` 的工具，它们更快、更可扩展，并且更好地解决了[碎片化](https://en.wikipedia.org/wiki/Fragmentation_(computing))[^20]问题。仅仅通过使用非标准内存分配器，你就可以获得 2% 左右的性能提升。动态内存分配的一个典型问题是，在启动时，线程会争相尝试同时分配内存区域。[^5] 最受欢迎的内存分配库之一是 jemalloc: [http://jemalloc.net/](http://jemalloc.net/)[^17] 和 tcmalloc: [https://github.com/google/tcmalloc](https://github.com/google/tcmalloc)[^18]。

其次，可以使用自定义分配器来加速分配，例如 arena 分配器: [https://en.wikipedia.org/wiki/Region-based_memory_management](https://en.wikipedia.org/wiki/Region-based_memory_management)[^16]。它们的主要优势之一是开销低，因为此类分配器不会为每次内存分配执行系统调用。另一个优点是它的高灵活性。开发人员可以根据操作系统提供的内存区域实现自己的分配策略。一个简单的方法是维护两个不同的分配器，每个分配器都有自己的 arena（内存区域）：一个用于热门数据，另一个用于冷数据。将热门数据放在一起可以使其共享缓存行，从而提高内存带宽利用率和空间局部性。它也改善了 TLB 利用率，因为热门数据占用的内存页面更少。此外，自定义内存分配器可以使用线程局部存储来实现每个线程的分配，并摆脱线程之间的任何同步。当应用程序基于线程池并且不会产生大量线程时，这变得很有用。

### 调整代码以适应内存层次结构

某些应用程序的性能取决于特定级别的缓存大小。这里最著名的例子是用 循环阻塞: [https://en.wikipedia.org/wiki/Loop_nest_optimization](https://en.wikipedia.org/wiki/Loop_nest_optimization)（平铺）改进矩阵乘法。这个想法是将矩阵的工作大小分解成更小的块（tiles），使每个块都适合 L2 缓存。[^9] 大多数架构提供类似 `CPUID` 的指令，[^11] 它允许我们查询缓存的大小。或者，可以使用 缓存无关算法: [https://en.wikipedia.org/wiki/Cache-oblivious_algorithm](https://en.wikipedia.org/wiki/Cache-oblivious_algorithm)[^19]，其目标是针对任何大小的缓存都能合理地工作。

英特尔 CPU 具有一个数据线性地址硬件功能 (见 [@sec:sec_PEBS_DLA])，支持缓存阻塞，如 easyperf 博客文章所述 [https://easyperf.net/blog/2019/12/17/Detecting-false-sharing-using-perf#2-tune-the-code-for-better-utilization-of-cache-hierarchy](https://easyperf.net/blog/2019/12/17/Detecting-false-sharing-using-perf#2-tune-the-code-for-better-utilization-of-cache-hierarchy)[^10]。

[^5]: 相同的情况也适用于内存释放。
[^6]: 行优先和列优先顺序 - [https://en.wikipedia.org/wiki/Row-_and_column-major_order](https://en.wikipedia.org/wiki/Row-_and_column-major_order)。
[^8]: 博客文章 "对象向量 vs 指针向量" 作者 B. Filipek - [https://www.bfilipek.com/2014/05/vector-of-objects-vs-vector-of-pointers.html](https://www.bfilipek.com/2014/05/vector-of-objects-vs-vector-of-pointers.html)。
[^9]: 通常情况下，人们会针对 L2 缓存的大小进行调整，因为它是内核之间不共享的。
[^10]: 博客文章 "检测伪共享" - [https://easyperf.net/blog/2019/12/17/Detecting-false-sharing-using-perf#2-tune-the-code-for-better-utilization-of-cache-hierarchy](https://easyperf.net/blog/2019/12/17/Detecting-false-sharing-using-perf#2-tune-the-code-for-better-utilization-of-cache-hierarchy)。
[^11]: 英特尔处理器的 `CPUID` 指令在 [[@IntelOptimizationManual](../References.md#IntelOptimizationManual), Volume 2] 中描述。
[^13]: Linux 手册页面，用于 `memalign` - [https://linux.die.net/man/3/memalign](https://linux.die.net/man/3/memalign)。
[^14]:生成对齐内存- [https://embeddedartistry.com/blog/2017/02/22/generating-aligned-memory/](https://embeddedartistry.com/blog/2017/02/22/generating-aligned-memory/)。
典型的`malloc`实现涉及同步，以防止多个线程试图动态分配内存
[^16]:基于区域的内存管理- [https://en.wikipedia.org/wiki/Region-based_memory_management](https://en.wikipedia.org/wiki/Region-based_memory_management)
[^17]: jemalloc - [http://jemalloc.net/] (http://jemalloc.net/)。
[^18]: tcmalloc - [https://github.com/google/tcmalloc](https://github.com/google/tcmalloc)
[^19]:缓存无关算法- [https://en.wikipedia.org/wiki/Cache-oblivious_algorithm](https://en.wikipedia.org/wiki/Cache-oblivious_algorithm)。
[^20]:碎片化- [https://en.wikipedia.org/wiki/Fragmentation_(computing)](https://en.wikipedia.org/wiki/Fragmentation_(computing))。
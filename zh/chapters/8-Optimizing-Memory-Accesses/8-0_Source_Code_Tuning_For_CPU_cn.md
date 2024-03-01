## 第二部分：源代码优化

欢迎来到本书的第二部分，我们将讨论各种低级源代码优化技术，也称为 *调优*。在第一部分，我们学习了如何找到代码中的性能瓶颈，这只是开发人员工作的一半。另一半是解决问题。

现代 CPU 是一个非常复杂的设备，几乎不可能预测某些代码片段的运行速度。软件和硬件性能取决于许多因素，移动部件的数量太多，超出人类思维的范围。幸运的是，通过本书第一部分讨论的所有性能监控功能，我们可以观察代码从 CPU 的角度如何运行。我们将广泛利用本书前面学到的方法和工具来指导我们的性能工程过程。

在非常高的层面上，软件优化可以分为五个类别。

* **算法优化**。理念：分析程序中使用的算法和数据结构，看看是否能找到更好的。示例：使用快速排序代替冒泡排序。
* **并行化计算**。理念：如果一个算法高度可并行化，使程序多线程化，或者考虑在 GPU 上运行。目标是同时做多件事。并发性已经在硬件和软件堆栈的所有层中使用。示例：将工作分布到多个线程上，平衡数据中心多个服务器之间的负载，使用异步 IO 以避免在等待 IO 操作时阻塞，保持多个并发网络连接以重叠请求延迟。
* **消除冗余工作**。理念：不要做你不需要的或已经完成的工作。示例：利用更多 RAM 来减少 CPU 和 IO 的使用量（缓存、记忆化、查找表、压缩），预计算已知编译时值，将循环不变计算移出循环，传引用 C++ 对象以避免传值引起的过度复制。
* **批量处理**。理念：聚合多个类似的操作并一次性执行，从而减少重复操作的开销。示例：发送较大的 TCP 数据包而不是许多小的数据包，分配大块内存而不是为数百个微小对象分配空间。
* **排序**。理念：重新排序算法中的操作序列。示例：更改数据布局以启用顺序内存访问，根据 C++ 多态对象的类型对数组进行排序以更好地预测虚函数调用，将热门函数分组并将其放置在二进制文件中更近的位置。

本书讨论的许多优化属于多个类别。例如，我们可以说向量化是并行化和批量处理的结合；循环阻塞（tiling）是批量处理和消除冗余工作的体现。

为了使图片完整，让我们也列出其他一些也许明显但仍然相当合理的加速方法：

* **使用另一种语言重写代码**：如果程序是用解释性语言（python、javascript 等）编写的，将其性能关键部分重写成开销更少的语言，例如 C++、Rust、Go 等。
* **调整编译器选项**：检查您是否至少使用了以下三个编译器标志：`-O3`（启用与机器无关的优化）、`-march`（启用针对特定 CPU 架构的优化）、`-flto`（启用过程间优化）。但不要就此止步，还有许多其他选项会影响性能。我们将在以后的章节中研究一些。可以考虑挖掘最佳选项集应用程序，可用的商业产品可以自动完成此过程。
* **优化第三方软件包**：绝大多数软件项目利用专有和开源代码层。这包括操作系统、库和框架。您还可以通过替换、修改或重新配置其中之一来寻求改进。
* **购买更快的硬件**：显然，这是一个与成本相关的业务决策，但有时它是其他选项都已用尽时唯一提高性能的方法。当您识别出应用程序中的性能瓶颈并清楚地传达给上层管理人员时，购买硬件更容易获得批准。例如，一旦您发现内存带宽限制了您的多线程程序的性能，您可能会建议购买具有更多内存通道和 DIMM 插槽的服务器主板和处理器。

### 算法优化 

标准算法和数据结构并不总是适用于性能关键型工作负载。例如，链接列表基本上已被淘汰，取而代之的是“扁平”数据结构。传统上，链接列表的每个新节点都是动态分配的。除了可能调用许多昂贵的内存分配之外，这可能导致列表的所有元素都分散在内存中。遍历这样的数据结构不利于缓存。尽管算法复杂度仍然是 O(N)，但实际上，其运行时间会比普通数组差得多。一些数据结构，比如二叉树，有自然链表式的表示，所以用指针追逐的方式实现它们可能很诱人。然而，存在更高效的“扁平”版本，参见 `boost::flat_map`、`boost::flat_set`。

在选择算法时，您可能会快速选择最流行的选项然后继续... 即使它可能不是您特定情况下的最佳选择。例如，您需要在已排序数组中找到一个元素。大多数开发人员考虑的第一个选项是二分搜索，对吧？它非常知名，并且在算法复杂度方面是最佳的，O(logN)。如果我告诉你数组保存 32 位整数，并且数组的大小通常很小（小于 20 个元素），你会改变你的决定吗？最终，测量应该指导您的决策，但二分搜索会受到分支预测错误的影响，因为每个元素值的测试都有 50% 的可能性为真。这就是为什么在小型数组上，即使线性扫描具有更差的算法复杂度，它通常也更快的原因。

### 数据驱动优化 

性能调优最重要的技术之一称为“数据驱动”优化，它基于程序处理的数据进行内省。该方法侧重于数据的布局及其在整个程序中的转换。这种方法的一个经典例子是数组结构到结构数组的转换，如 [@lst:AOStoSOA](#AOStoSOA) 所示。

代码清单：SOA 到 AOS 转换。 
<div id="AOStoSOA"></div>

``` cpp
struct S {
  int a;
  int b;
  int c;
  // other fields
};
S s[N];    // AOS

<=>
    
struct S { // SOA
  int a[N];
  int b[N];
  int c[N];
  // other fields  
};
```

数据驱动开发 (DDD) 的主要思想是研究程序如何访问数据（数据在内存中的布局，访问模式），然后相应地修改程序（改变数据布局，改变访问模式）。

> [!TIP|style:flat|label:作者个人经验]
> 实际上，我们可以说所有的优化在某种程度上都是数据驱动的。即使是我们将在下一节看到的转换，也是基于我们从程序执行中获得的一些反馈：函数调用次数，分支是否被采取，性能计数器等。

DDD 的另一个广泛示例是“小尺寸优化”。它的想法是静态预分配一定量的内存来避免动态内存分配。对于元素上限可以很好预测的中小型容器来说，它尤其有用。现代 C++ STL 的 `std::string` 实现将前 15-20 个字符保存在堆栈上分配的缓冲区中，只有更长的字符串才会在堆上分配内存。LLVM 的 `SmallVector` 和 Boost 的 `static_vector` 也是这种方法的其他例子。

### 低级优化 

性能工程是一种艺术。就像任何艺术一样，可能的情况是无穷无尽的。不可能涵盖所有可以想象的优化。接下来的几个章节主要讨论针对现代 CPU 架构的优化。

在我们跳入特定的源代码优化技术之前，需要做一些注意事项。首先，避免优化糟糕的代码。如果一段代码存在高级性能低下问题，你不应该对其应用机器特定的优化。始终先关注修复主要问题。只有当你确定算法和数据结构针对你要解决的问题是最佳的，然后尝试应用低级改进。

其次，请记住，您实施的优化可能并非在所有平台上都受益。例如，循环阻塞取决于系统内存层次结构的特征，尤其是 L2 和 L3 缓存的大小。因此，针对具有特定 L2 和 L3 缓存大小的 CPU 调整的算法可能无法很好地适用于缓存更小的 CPU。在您的应用程序将运行的平台上测试更改很重要。

接下来的四章按照 TMA 分类进行组织（参见 [@sec:TMA]):

* 第 8 章. 优化内存访问 - `TMA:MemoryBound` 类别
* 第 9 章. 优化计算 - `TMA:CoreBound` 类别
* 第 10 章. 优化分支预测 - `TMA:BadSpeculation` 类别
* 第 11 章. 机器代码布局优化 - `TMA:FrontEndBound` 类别

此分类背后的思想是为使用 TMA 方法进行性能工程工作的开发人员提供一个清单。每当 TMA 将性能瓶颈归因于上述类别之一时，您可以随时参考相应的章节以了解您的选项。

第 14 章涵盖了不属于上述任何类别的其他优化领域。第 15 章解决了一些优化多线程应用程序中常见的难题。
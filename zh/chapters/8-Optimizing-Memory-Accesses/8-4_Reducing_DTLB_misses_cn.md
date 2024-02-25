## 减少 DTLB 未命中 {#sec:secDTLB}

正如本书前面所述，TLB 是一个快速但有限的每个内核缓存，用于将内存地址的虚拟到物理地址转换。如果没有它，应用程序每次内存访问都需要耗时的内核页表遍历来计算每个引用虚拟地址的正确物理地址。在具有 5 级页表的系统中，它将需要访问至少 5 个不同的内存位置才能获得地址转换。在 [@sec:FeTLB] 部分，我们将讨论如何将大页面用于代码。在这里，我们将看到它们如何用于数据。

任何随机访问大内存区域的算法都可能遭受 DTLB 未命中之苦。这类应用程序的例子包括：在大数组中进行二进制搜索，访问大型哈希表，遍历图。使用大页面有可能加速这类应用程序。

在 x86 平台上，默认页面大小为 4KB。考虑一个应用程序主动引用数百 MB 的内存。首先，它需要分配许多小页面，这代价很高。其次，它将触及许多 4KB 大小的页面，每个页面都将在有限的一组 TLB 条目中竞争。例如，使用 2MB 的大页面，可以使用仅仅十个页面映射 20MB 的内存，而使用 4KB 的页面，您将需要 5120 个页面。这意味着需要的 TLB 条目更少，从而减少了 TLB 未命中次数。由于 2MB 条目的数量少得多，因此不会按 512 的比例减少。例如，在英特尔的 Skylake 内核系列中，L1 DTLB 为 4KB 页面提供 64 个条目，为 2MB 页面仅提供 32 个条目。除了 2MB 的大页面，AMD 和英特尔的 x86 架构芯片还支持 1GB 的超大页面，这些页面仅可用于数据，不能用于指令。使用 1GB 页面而不是 2MB 页面可以进一步减少 TLB 压力。

使用大页面通常会导致更少的页面遍历，并且在 TLB 未命中情况下遍历内核页表的惩罚也会减少，因为表本身更加紧凑。利用大页面的性能提升有时可以高达 30%，具体取决于应用程序遇到的 TLB 压力有多大。期望 2 倍的加速会要求太高，因为 TLB 未命中是主要瓶颈的情况相当罕见。论文 [[@Luo2015](../References.md#Luo2015)] 介绍了在 SPEC2006 benchmark 套件上使用大页面的评估。结果可以总结如下。在套件中的 29 个基准测试中，有 15 个的加速在 1% 以内，可以忽略不计。六个基准测试的加速范围在 1%-4% 之间。四个基准测试的加速范围在 4% 到 8% 之间。两个基准测试的加速分别为 10%，而获得最大收益的两个基准测试分别享受了 22% 和 27% 的加速。

许多现实世界的应用程序已经利用了大页面，例如 KVM、MySQL、PostgreSQL、Java JVM 等。通常，这些软件包提供了一个启用该功能的选项。每当您使用类似应用程序时，请查看其文档，了解是否可以启用大页面。

Windows 和 Linux 都允许应用程序建立大页面内存区域。有关如何在 Windows 和 Linux 上启用大页面的说明，请参见附录 C。在 Linux 上，应用程序中有两种使用大页面的方式：显式大页面和透明大页面。Windows 的支持不像 Linux 那么丰富，将在以后讨论。

### 显式大页面 (EHP)。

显式大页面 (EHP) 是系统内存的一部分，作为大页面文件系统 `hugetlbfs` 暴露。顾名思义，EHP 应在启动时或运行时预留。有关如何操作的说明，请参见附录 C。在启动时预留 EHP 可以增加分配成功的可能性，因为内存尚未严重碎片化。显式预分配的页面驻留在预留的内存块中，并且在内存压力下无法换出。此外，该内存空间无法用于其他目的，因此用户应谨慎分配，仅预留他们需要的页面数量。

在应用程序中使用 EHP 的最简单方法是在 `mmap` 中调用 `MAP_HUGETLB`，如 [@lst:ExplicitHugepages1] 所示。在此代码中，指针 `ptr` 将指向一个 2MB 的内存区域，该区域是显式预留给 EHP 的。请注意，由于 EHP 没有预先保留，分配可能会失败。应用程序中使用 EHP 的另一种不太流行的方法可以在附录 C 中找到。此外，开发人员可以编写自己的基于 arena 的分配器，利用 EHP 进行分配。

代码清单:从显式分配的巨大页面映射内存区域。

~~~~ {#lst:ExplicitHugepages1 .cpp}
void ptr = mmap(nullptr, size, PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0);
if (ptr == MAP_FAILED)
  throw std::bad_alloc{};                
...
munmap(ptr, size);
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

过去，可以使用 libhugetlbfs: [https://github.com/libhugetlbfs/libhugetlbfs](https://github.com/libhugetlbfs/libhugetlbfs)[^1] 库，该库允许覆盖现有动态链接的可执行文件使用的 `malloc` 调用，从而在大页面 (EHP) 之上分配内存。不幸的是，此项目已不再维护。它不需要用户修改代码或重新链接二进制文件。他们只需用 `LD_PRELOAD=libhugetlbfs.so HUGETLB_MORECORE=yes <your app command line>` 预先填充命令行即可使用它。但幸运的是，还有其他库允许使用大页面（非 EHP）和 `malloc`，我们稍后会看到。

### 透明大页面 (THP)

Linux 还提供透明大页面支持 (THP)，它具有两种操作模式：系统范围和每个进程。启用系统范围的 THP 时，内核会自动管理大页面，这对应用程序是透明的。操作系统内核尝试在需要大量内存块时将大页面分配给任何进程，并且如果可以分配这样的页面，则无需手动保留大页面。如果启用每个进程的 THP，内核仅将大页面分配给单个进程的内存区域，这些区域归因于 `madvise` 系统调用。您可以使用以下命令检查系统中是否启用了 THP：

```bash
$ cat /sys/kernel/mm/transparent_hugepage/enabled
always [madvise] never
```

如果值为 `always` (系统范围) 或 `madvise` (每个进程)，则 THP 可供您的应用程序使用。有关每个选项的详细规范，请参见 Linux内核文档 [^2] 中关于 THP 的内容。

启用系统范围的 THP 时，将自动将大页面用于常规内存分配，而无需应用程序明确请求。基本上，要观察大页面对应用程序的影响，用户只需启用系统范围的 THP，使用 `echo "always" | sudo tee /sys/kernel/mm/transparent_hugepage/enabled` 即可。它将自动启动名为 `khugepaged` 的守护进程，该进程开始扫描应用程序的内存空间，将普通页面提升为大页面。不过，有时内核可能无法将普通页面提升为大页面，因为找不到 2MB 的连续内存块。

[TODO]: 在我的系统上，看起来 `khugepaged` 没有执行这项工作，而是采用了不同的行为：我的应用程序在分配失败时会暂停，并立即回收普通页面并将它们提升为 THP。

系统范围的 THP 模式适用于快速实验，以检查大页面是否能提高性能。它可以自动工作，即使对于不知道 THP 的应用程序也是如此，因此开发人员不必更改代码即可看到大页面对他们应用程序的好处。

启用系统范围的大页面时，应用程序最终可能会分配更多的内存资源。应用程序可能会映射一个大区域，但只触碰其中 1 个字节，在这种情况下，可能会分配一个 2MB 的页面而不是 4k 的页面，这毫无意义。这就是为什么可以禁用系统范围的 THP，只让它们存在于 MADV_HUGEPAGE madvise 区域中，我们将在下面讨论这一点。完成实验后，请记得禁用系统范围的 THP，因为它可能不会使系统上运行的每个应用程序都受益。

使用 `madvise`（每个进程）选项时，THP 仅在通过 `madvise` 系统调用并带有 `MADV_HUGEPAGE` 标志的内存区域内启用。如 [@lst:TransparentHugepages1] 所示，指针 `ptr` 将指向一个 2MB 的匿名（透明）内存区域，该区域由内核动态分配。如果内核找不到 2MB 的连续内存块，`mmap` 调用可能会失败。

代码清单:将内存区域映射到一个透明的巨大页面。

~~~~ {#lst:TransparentHugepages1 .cpp}
void ptr = mmap(nullptr, size, PROT_READ | PROT_WRITE | PROT_EXEC,
                MAP_PRIVATE | MAP_ANONYMOUS, -1 , 0);
if (ptr == MAP_FAILED)
  throw std::bad_alloc{};
madvise(ptr, size, MADV_HUGEPAGE);
// use the memory region `ptr`
munmap(ptr, size);
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

开发人员可以根据 [@lst:TransparentHugepages1] 中的代码构建自定义 THP 分配器。但是，他们还可以将 THP 用于应用程序进行的 `malloc` 调用中。许多内存分配库通过覆盖 `libc` 的 `malloc` 实现来提供此功能。以下是最流行的此类库之一 `jemalloc` 的示例。

如果您拥有应用程序的源代码，则可以使用附加的 `-ljemalloc` 选项重新链接二进制文件。这将使您的应用程序与 `jemalloc` 库动态链接，该库将处理所有 `malloc` 调用。然后使用以下选项启用堆分配的 THP：

```bash
$ MALLOC_CONF="thp:always" <your app command line>
```

如果您没有源代码，仍然可以通过预加载动态库来利用 `jemalloc`：

```bash
$ LD_PRELOAD=/usr/local/libjemalloc.so.2 MALLOC_CONF="thp:always" <your app command line>
```

Windows 只提供类似于 Linux THP 每个进程模式的方式使用大页面，通过 WinAPI `VirtualAlloc` 系统调用。有关详细信息，请参见附录 C。

### 显式大页面 (EHP) vs. 透明大页面 (THP)

Linux 用户可以使用三种不同的模式使用大页面：

* 显式大页面 (EHP)
* 系统范围透明大页面 (THP)
* 每个进程透明大页面 (THP)

让我们比较一下这些选项。首先，EHP 预先保留在虚拟内存中，而 THP 则没有。这使得使用 EHP 的软件包更难以交付，因为它们依赖于机器管理员所做的特定配置设置。此外，EHP 静态驻留在内存中，占用宝贵的 DRAM 空间，即使它们未使用。

其次，系统范围的透明大页面非常适合快速实验。无需更改用户代码即可测试在您的应用程序中使用大页面的好处。但是，将软件包运送给客户并要求他们启用系统范围的 THP 是不明智的，因为这可能会对该系统上运行的其他程序产生负面影响。通常，开发人员会识别代码中可以从大页面中受益的分配，并在这些位置使用 `madvise` 提示（每个进程模式）。

每个进程的 THP 没有上述任何一个缺点，但它还有一个缺点。之前我们讨论过，内核分配 THP 对用户来说是透明的。分配过程可能涉及多个内核进程，这些进程负责在虚拟内存中腾出空间，这可能包括将内存换出到磁盘、碎片化或提升页面。透明大页面的后台维护会产生内核在管理不可避免的碎片和交换问题时产生的非确定性延迟开销。EHP 不受内存碎片化影响，也不能换出到磁盘，因此延迟开销要小得多。

总而言之，THP 更易于使用，但会产生更大的分配延迟开销。这正是 THP 在高频交易和其他超低延迟行业不受欢迎的原因，他们更喜欢使用 EHP。另一方面，虚拟机提供商和数据库往往倾向于使用每个进程的 THP，因为要求额外的系统配置会给他们的用户带来负担。

[^1]: libhugetlbfs - [https://github.com/libhugetlbfs/libhugetlbfs](https://github.com/libhugetlbfs/libhugetlbfs).
[^2]: Linux kernel THP documentation - [https://www.kernel.org/doc/Documentation/vm/transhuge.txt](https://www.kernel.org/doc/Documentation/vm/transhuge.txt)

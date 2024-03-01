# 附录 C. 启用大页面 (.unnumbered)



## Windows

要在 Windows 上使用大页面，需要启用 `SeLockMemoryPrivilege` 安全策略 (链接到微软文档: [https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/lock-pages-in-memory](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/lock-pages-in-memory)). 这可以通过 Windows API 以编程方式完成，也可以通过安全策略 GUI 完成。

1. 点击开始 -> 搜索 "secpol.msc"，启动它。
2. 在左侧选择 "本地策略" -> "用户权利分配"，然后双击 "锁定内存中的页面"。

Windows 安全：锁定内存中的页面: https://raw.githubusercontent.com/dendibakh/perf-book/main/img/appendix-C/WinLockPages.png

3. 添加您的用户并重新启动机器。

4. 使用 RAMMap: [https://docs.microsoft.com/en-us/sysinternals/downloads/rammap](https://docs.microsoft.com/en-us/sysinternals/downloads/rammap) 工具检查运行时是否使用了大页面。

在代码中使用大页面：

```c++
void* p = VirtualAlloc(NULL, size, MEM_RESERVE | 
                                   MEM_COMMIT | 
                                   MEM_LARGE_PAGES,
                       PAGE_READWRITE);
...
VirtualFree(ptr, 0, MEM_RELEASE);
```

## Linux

在 Linux 操作系统上，应用程序可以使用大页面的两种方式：显式和大页面透明分配。

### 显式大页面 (.unnumbered)

显式大页面可以在启动时或运行时预留。要在启动时强制 Linux内核分配 128 个大页面，请运行以下命令：

```bash
$ echo "vm.nr_hugepages = 128" >> /etc/sysctl.conf
```

要显式分配固定数量的大页面，可以使用 libhugetlbfs: [https://github.com/libhugetlbfs/libhugetlbfs](https://github.com/libhugetlbfs/libhugetlbfs)。以下命令预分配 128 个大页面。

```bash
$ sudo apt install libhugetlbfs-bin
$ sudo hugeadm --create-global-mounts
$ sudo hugeadm --pool-pages-min 2M:128
```

这大致相当于执行以下命令，不需要 libhugetlbfs（参见内核文档：链接到内核文档: [https://www.kernel.org/doc/Documentation/vm/hugetlbpage.txt](https://www.kernel.org/doc/Documentation/vm/hugetlbpage.txt)):

```bash
$ echo 128 > /proc/sys/vm/nr_hugepages
$ mount -t hugetlbfs                                                      \
    -o uid=<value>,gid=<value>,mode=<value>,pagesize=<value>,size=<value>,\
    min_size=<value>,nr_inodes=<value> none /mnt/huge
```

您应该可以在 `/proc/meminfo` 中观察到效果。请注意，这是一个系统范围的视图，而不是针对每个进程：

```bash
$ watch -n1 "cat /proc/meminfo  | grep huge -i"
AnonHugePages:      2048 kB
ShmemHugePages:        0 kB
FileHugePages:         0 kB
HugePages_Total:     128    <== 128 huge pages allocated
HugePages_Free:      128
HugePages_Rsvd:        0
HugePages_Surp:        0
Hugepagesize:       2048 kB
Hugetlb:          262144 kB <== 256MB of space occupied
```

开发人员可以在代码中通过调用带有 `MAP_HUGETLB` 标志的 `mmap` 来利用显式大页面（[完整示例](https://github.com/torvalds/linux/blob/master/tools/testing/selftests/vm/map_hugetlb.c)[^25]）：

```c++
void ptr = mmap(nullptr, size, PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0);
...
munmap(ptr, size);
```

其他替代方案包括：

* 使用来自已挂载的 `hugetlbfs` 文件系统的文件进行 `mmap` ([示例代码](https://github.com/torvalds/linux/blob/master/tools/testing/selftests/vm/hugepage-mmap.c)[^26])。
* 使用 `SHM_HUGETLB` 标志的 `shmget` ([示例代码](https://github.com/torvalds/linux/blob/master/tools/testing/selftests/vm/hugepage-shm.c)[^27]).

## 透明大页内存 

要在 Linux 上允许应用程序使用透明大页 (THP)，需要确保 `/sys/kernel/mm/transparent_hugepage/enabled` 设置为 `always` 或 `madvise`。 前者启用系统范围的 THP 使用，而后者则将对哪些内存区域应使用 THP 的控制权交给用户代码，从而避免消耗更多内存资源的风险。 以下是使用 `madvise` 方法的示例：

```c++
void ptr = mmap(nullptr, size, PROT_READ | PROT_WRITE | PROT_EXEC,
                MAP_PRIVATE | MAP_ANONYMOUS, -1 , 0);
madvise(ptr, size, MADV_HUGEPAGE);
...
munmap(ptr, size);
```

您可以在 `/proc/meminfo` 下的 `AnonHugePages` 中观察到系统范围的效果：

```bash
$ watch -n1 "cat /proc/meminfo  | grep huge -i" 
AnonHugePages:     61440 kB     <== 30 transparent huge pages are in use
HugePages_Total:     128
HugePages_Free:      128        <== explicit huge pages are not used
```

此外，开发人员可以通过查看针对其进程的特定 `smaps` 文件来观察其应用程序如何利用 EHP 和/或 THP：

```bash
$ watch -n1 "cat /proc/<PID_OF_PROCESS>/smaps"
```

[^25]: MAP_HUGETLB 示例 - [https://github.com/torvalds/linux/blob/master/tools/testing/selftests/vm/map_hugetlb.c](https://github.com/torvalds/linux/blob/master/tools/testing/selftests/vm/map_hugetlb.c).
[^26]: 已挂载的 `hugetlbfs` 文件系统 - [https://github.com/torvalds/linux/blob/master/tools/testing/selftests/vm/hugepage-mmap.c](https://github.com/torvalds/linux/blob/master/tools/testing/selftests/vm/hugepage-mmap.c).
[^27]: SHM_HUGETLB 示例 - [https://github.com/torvalds/linux/blob/master/tools/testing/selftests/vm/hugepage-shm.c](https://github.com/torvalds/linux/blob/master/tools/testing/selftests/vm/hugepage-shm.c).

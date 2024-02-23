---
typora-root-url: ..\..\img
---

## 缓存失效

正如在[@sec:MemHierar]中讨论的那样，任何在特定级别的缓存中缺失的内存请求都必须由更高级别的缓存或DRAM进行服务。这意味着这种内存访问的延迟会显著增加。内存子系统组件的典型延迟如表{@tbl:mem_latency}所示。还有一个[交互视图](https://colin-scott.github.io/personal_website/research/interactive_latency.html)[^1]，可视化了现代系统中不同操作的延迟。性能会受到严重影响，特别是当内存请求在最后一级缓存（LLC）中丢失并一直到达主存时。英特尔® [Memory Latency Checker](https://www.intel.com/software/mlc)[^2]（MLC）是用于测量内存延迟和带宽以及它们随系统负载增加而变化的工具。MLC对于建立测试系统的基准和进行性能分析非常有用。当我们讨论[@sec:MemLatBw]中的内存延迟和带宽时，我们将使用这个工具。

-------------------------------------------------
内存层次结构组件          延迟（周期/时间）

--------------------------   --------------------
L1缓存                      4个周期（~1纳秒）

L2缓存                      10-25个周期（5-10纳秒）

L3缓存                      ~40个周期（20纳秒）

主内存                      200个周期以上（100纳秒）

-------------------------------------------------

表：x86平台内存子系统的典型延迟。{#tbl:mem_latency}

缓存失效可能会发生在指令和数据上。根据Top-down Microarchitecture Analysis（见[@sec:TMA]），指令缓存（I-cache）失效被定义为前端停顿，而数据缓存（D-cache）失效被定义为后端停顿。指令缓存失效在CPU流水线的早期阶段（指令获取阶段）发生。数据缓存失效则发生在后期，即指令执行阶段。

Linux `perf`用户可以通过运行以下命令来收集L1缓存失效的数量：

```bash
$ perf stat -e mem_load_retired.fb_hit,mem_load_retired.l1_miss,
  mem_load_retired.l1_hit,mem_inst_retired.all_loads -- a.exe
   29580  mem_load_retired.fb_hit
   19036  mem_load_retired.l1_miss
  497204  mem_load_retired.l1_hit
  546230  mem_inst_retired.all_loads
```

以上是针对L1数据缓存和填充缓冲区的所有加载操作的细分。加载操作可能命中已分配的填充缓冲区（`fb_hit`），或者命中L1缓存（`l1_hit`），或者两者都未命中（`l1_miss`），因此 `all_loads = fb_hit + l1_hit + l1_miss`。我们可以看到，只有3.5%的所有加载操作在L1缓存中未命中，因此*L1命中率*为96.5%。

我们可以进一步分析L1数据缺失并分析L2缓存行为，方法是运行：

```bash
$ perf stat -e mem_load_retired.l1_miss,
  mem_load_retired.l2_hit,mem_load_retired.l2_miss -- a.exe
  19521  mem_load_retired.l1_miss
  12360  mem_load_retired.l2_hit
   7188  mem_load_retired.l2_miss
```

从这个例子中，我们可以看到，在L1 D-cache中缺失的加载操作中有37%也在L2缓存中缺失，因此*L2命中率*为63%。以类似的方式，可以对L3缓存进行细分。


[^1]: 交互延迟 - [https://colin-scott.github.io/personal_website/research/interactive_latency.html](https://colin-scott.github.io/personal_website/research/interactive_latency.html)
[^2]: Memory Latency Checker - [https://www.intel.com/software/mlc](https://www.intel.com/software/mlc)
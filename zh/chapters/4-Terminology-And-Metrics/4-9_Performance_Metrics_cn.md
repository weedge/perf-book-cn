## 性能指标 {#sec:PerfMetrics}

除了本章前面讨论的性能事件外，性能工程师经常使用基于原始事件的指标。表{@tbl:perf_metrics}显示了针对英特尔第12代Goldencove架构的一系列指标，包括描述和公式。该列表并非详尽无遗，但显示了最重要的指标。有关英特尔CPU及其公式的完整指标列表可在[TMA_metrics.xlsx](https://github.com/intel/perfmon/blob/main/TMA_Metrics.xlsx)中找到。[@sec:PerfMetricsCaseStudy]展示了如何在实践中使用性能指标。


| 指标名称 | 描述 | 公式 |
|---|---|---|
| L1MPKI | 每千条已退休需求负载指令的 L1 缓存真未命中数量 | 1000 * MEM_LOAD_RETIRED.L1_MISS_PS / INST_RETIRED.ANY |
| L2MPKI | 每千条已退休需求负载指令的 L2 缓存真未命中数量 | 1000 * MEM_LOAD_RETIRED.L2_MISS_PS / INST_RETIRED.ANY |
| L3MPKI | 每千条已退休需求负载指令的 L3 缓存真未命中数量 | 1000 * MEM_LOAD_RETIRED.L3_MISS_PS / INST_RETIRED.ANY |
| Branch Mispr. Ratio | 所有分支的误判率 | BR_MISP_RETIRED.ALL_BRANCHES / BR_INST_RETIRED.ALL_BRANCHES |
| Code STLB MPKI | STLB (2 级 TLB) 代码推测性未命中每千条指令 | 1000 * ITLB_MISSES.WALK_COMPLETED / INST_RETIRED.ANY |
| Load STLB MPKI | STLB 数据加载推测性未命中每千条指令 | 1000 * DTLB_LOAD_MISSES.WALK_COMPLETED / INST_RETIRED.ANY |
| Store STLB MPKI | STLB 数据存储推测性未命中每千条指令 | 1000 * DTLB_STORE_MISSES.WALK_COMPLETED / INST_RETIRED.ANY |
| Load Miss Real Latency | L1 数据缓存未命中需求负载操作的实际平均延迟（核心周期） | L1D_PEND_MISS.PENDING / MEM_LOAD_COMPLETED.L1_MISS_ANY |
| ILP | 每内核指令级并行性（当存在执行时，平均执行的 μops 数量） | UOPS_EXECUTED.THREAD / UOPS_EXECUTED.CORE_CYCLES_GE_1，如果启用 SMT，则除以 2 |
| MLP | 每线程内存级并行性（当至少有一个这样的未命中时，L1 未命中需求负载的平均数量） | L1D_PEND_MISS.PENDING / L1D_PEND_MISS.PENDING_CYCLES |
| DRAM BW Use | 平均外部内存带宽使用（读写 GB/秒） | ( 64 * ( UNC_M_CAS_COUNT.RD + UNC_M_CAS_COUNT.WR ) / 1GB ) / 时间 |
| IpCall | 近调用每条指令 | INST_RETIRED.ANY / BR_INST_RETIRED.NEAR_CALL |
| Ip Branch | 每分支指令 | INST_RETIRED.ANY / BR_INST_RETIRED.ALL_BRANCHES |
| IpLoad | 每加载指令 | INST_RETIRED.ANY / MEM_INST_RETIRED.ALL_LOADS_PS |
| IpStore | 每存储指令 | INST_RETIRED.ANY / MEM_INST_RETIRED.ALL_STORES_PS |
| IpMisp | 每非推测分支误判指令 | INST_RETIRED.ANY / BR_MISP_RETIRED.ALL_BRANCHES |
| IpFLOP | 每浮点 (FP) 操作指令 | 请参阅 TMA_metrics.xlsx |
| IpArith Scalar SP | 每标量单精度 FP 算术指令 | INST_RETIRED.ANY / FP_ARITH_INST_RETIRED.SCALAR_SINGLE |
| IpArith Scalar DP | 每标量双精度 FP 算术指令 | INST_RETIRED.ANY / FP_ARITH_INST_RETIRED.SCALAR_DOUBLE |
| Ip Arith AVX128 | 每 FP 算术 AVX128 128 位指令 | INST_RETIRED.ANY / (FP_ARITH_INST_RETIRED.128B_PACKED_DOUBLE + FP_ARITH_INST_RETIRED.128B_PACKED_SINGLE) |
| Ip Arith AVX256 | 每 FP 算术 AVX256 256 位指令 | INST_RETIRED.ANY / ( FP_ARITH_INST_RETIRED.256B_PACKED_DOUBLE+ FP_ARITH_INST_RETIRED.256B_PACKED_SINGLE) |
| Ip SWPF | 每个软件预取指令 (of any type) | INST_RETIRED.ANY / SW_PREFETCH_ACCESS.T0:u0xF |

Table：英特尔Goldencove架构的一系列次要指标及其描述和公式（非详尽）。 {#tbl:perf_metrics}

关于这些指标的一些说明。首先，ILP和MLP指标并不代表应用程序的理论最大值；而是衡量在给定机器上应用程序的实际ILP和MLP。在具有无限资源的理想机器上，这些数字会更高。其次，除了"DRAM BW Use"和"Load Miss Real Latency"之外的所有指标都是分数；我们可以对每个指标进行相当直接的推理，以确定特定指标是高还是低。但要理解"DRAM BW Use"和"Load Miss Real Latency"指标的意义，我们需要将其放在一个上下文中。对于前者，我们想知道一个程序是否饱和了内存带宽。后者为你提供了缓存失效的平均成本，但这本身是无用的，除非你知道缓存层次结构中每个组件的延迟。我们将在下一节讨论如何找出缓存延迟和峰值内存带宽。

一些工具可以自动报告性能指标。如果没有，你总可以手动计算这些指标，因为你知道公式和必须收集的相应性能事件。表{@tbl:perf_metrics}提供了针对英特尔Goldencove架构的公式，但只要底层的性能事件可用，你就可以在另一个平台上构建类似的指标。
# 摘要

* [README.md](README.md)

## 0.前言 Preface
* [0-1.通告](./chapters/0-Preface/0-1_Notices_cn.md)
* [0-2.前言](./chapters/0-Preface/0-2_Preface_cn.md)
* [0-3.致谢](./chapters/0-Preface/0-3_Acknowledgements_cn.md)

## 1.介绍 Introduction
* [1-0.介绍](./chapters/1-Introduction/1-0_Introduction_cn.md)
* [1-1.为什么需要性能调优？](./chapters/1-Introduction/1-1_Why_do_we_need_perf_analysis_cn.md)
* [1-2.谁需要性能调优？](./chapters/1-Introduction/1-2_Who_needs_performance_analysis_cn.md)
* [1-3.什么是性能分析？](./chapters/1-Introduction/1-3_What_is_performance_analysis_cn.md)
* [1-4.本书讨论了什么？](./chapters/1-Introduction/1-4_What_is_in_the_book_cn.md)
* [1-5.本书未涉及的内容](./chapters/1-Introduction/1-5_What_is_not_in_this_book_cn.md)
* [1-6.练习](./chapters/1-Introduction/1-6_Exercises_cn.md)
* [1-7.章节总结](./chapters/1-Introduction/1-7_Chapter_Summary_cn.md)

## 2.性能测量 Measuring-Performance
* [2-0.性能测量](./chapters/2-Measuring-Performance/2-0_Measuring_Performance_cn.md)
* [2-1.现代系统中的噪声](./chapters/2-Measuring-Performance/2-1_Noise_In_Modern_Systems_cn.md)
* [2-2.在生产环境中进行性能测量](./chapters/2-Measuring-Performance/2-2_Measuring_Performance_In_Procution_cn.md)
* [2-3.自动检测性能回归](./chapters/2-Measuring-Performance/2-3_Performance_Regressions_cn.md)
* [2-4.本地性能测量](./chapters/2-Measuring-Performance/2-4_Local_Performance_Testing_cn.md)
* [2-5.软件和硬件定时器](./chapters/2-Measuring-Performance/2-5_SW_and_HW_Timers_cn.md)
* [2-6.微基准测试](./chapters/2-Measuring-Performance/2-6_Microbenchmarks_cn.md)
* [2-7.问题和练习](./chapters/2-Measuring-Performance/2-7_Questions-Exercises_cn.md)
* [2-8.章节总结](./chapters/2-Measuring-Performance/2-8_Chapter_summary_cn.md)

## 3.CPU微体系结构 CPU-Microarchitecture
* [3-0.CPU微体系结构](./chapters/3-CPU-Microarchitecture/3-0_CPU_microarchitecture_cn.md)
* [3-1.指令集架构](./chapters/3-CPU-Microarchitecture/3-1_ISA_cn.md)
* [3-2.流水线技术](./chapters/3-CPU-Microarchitecture/3-2_Pipelining_cn.md)
* [3-3.开发指令级并行性](./chapters/3-CPU-Microarchitecture/3-3_Exploiting_ILP_cn.md)
* [3-4.SIMD](./chapters/3-CPU-Microarchitecture/3-4_SIMD_cn.md)
* [3-5.开发线程级并行性](./chapters/3-CPU-Microarchitecture/3-5_Exploiting_TLP_cn.md)
* [3-6.存储器层次结构](./chapters/3-CPU-Microarchitecture/3-6_Memory_Hierarchy_cn.md)
* [3-7.虚拟内存](./chapters/3-CPU-Microarchitecture/3-7_Virtual_memory_cn.md)
* [3-8.现代CPU设计](./chapters/3-CPU-Microarchitecture/3-8_Modern_CPU_design_cn.md)
* [3-9.性能监控单元](./chapters/3-CPU-Microarchitecture/3-9_PMU_cn.md)
* [3-10.问题和练习](./chapters/3-CPU-Microarchitecture/3-10_Questions-Exercises_cn.md)
* [3-11.章节总结](./chapters/3-CPU-Microarchitecture/3-11_Chapter_summary_cn.md)

## 4.性能分析中的术语和指标 Terminology-And-Metrics
* [4-0.性能分析中的术语和指标](./chapters/4-Terminology-And-Metrics/4-0_Terminology_and_metrics_in_performance_analysis_cn.md)
* [4-1.已退役和已执行指令](./chapters/4-Terminology-And-Metrics/4-1_Retired_and_Executed_Instruction_cn.md)
* [4-2.CPU利用率](./chapters/4-Terminology-And-Metrics/4-2_CPU_Utilization_cn.md)
* [4-3.CPI 和 IPC](./chapters/4-Terminology-And-Metrics/4-3_CPI_and_IPC_cn.md)
* [4-4.微操作](./chapters/4-Terminology-And-Metrics/4-4_UOP_cn.md)
* [4-5.管道槽](./chapters/4-Terminology-And-Metrics/4-5_Pipeline_Slot_cn.md)
* [4-6.核心周期与参考周期](./chapters/4-Terminology-And-Metrics/4-6_Core_and_Reference_Cycles_cn.md)
* [4-7.缓存失效](./chapters/4-Terminology-And-Metrics/4-7_Cache_miss_cn.md)
* [4-8.错误预测的分支](./chapters/4-Terminology-And-Metrics/4-8_Mispredicted_branch_cn.md)
* [4-9.性能指标](./chapters/4-Terminology-And-Metrics/4-9_Performance_Metrics_cn.md)
* [4-10.内存延迟和带宽](./chapters/4-Terminology-And-Metrics/4-10_Memory_Latency_and_Bandwidth_cn.md)
* [4-11.案例研究：分析四个基准测试的性能指标 ](./chapters/4-Terminology-And-Metrics/4-11_Case_Study_of_4_Benchmarks_cn.md)
* [4-15.问题和练习](./chapters/4-Terminology-And-Metrics/4-15_Questions-Exercises_cn.md)
* [4-16.章节总结](./chapters/4-Terminology-And-Metrics/4-16_Chapter_summary_cn.md)

## 5.性能分析方法 Performance-Analysis-Approaches
* [5-0.性能分析方法](./chapters/5-Performance-Analysis-Approaches/5-0_Performance_analysis_approaches_cn.md)
* [5-1.代码仪器化](./chapters/5-Performance-Analysis-Approaches/5-1_Code_instrumentation_cn.md)
* [5-2.跟踪](./chapters/5-Performance-Analysis-Approaches/5-2_Tracing_cn.md)
* [5-3.工作负载特征化](./chapters/5-Performance-Analysis-Approaches/5-3_Characterization_cn.md)
* [5-4.使用标记器 API](./chapters/5-Performance-Analysis-Approaches/5-4_Marker_APIs_cn.md)
* [5-5.采样](./chapters/5-Performance-Analysis-Approaches/5-5_Sampling_cn.md)
* [5-6.Roofline 性能模型](./chapters/5-Performance-Analysis-Approaches/5-6_Roofline_cn.md)
* [5-7.静态性能分析](./chapters/5-Performance-Analysis-Approaches/5-7_Static_performance_analysis_cn.md)
* [5-8.编译器优化报告](./chapters/5-Performance-Analysis-Approaches/5-8_Compiler_Opt_Reports_cn.md)
* [5-9.问题和练习](./chapters/5-Performance-Analysis-Approaches/5-9_Questions-Exercises_cn.md)
* [5-10.章节总结](./chapters/5-Performance-Analysis-Approaches/5-10_Chapter_Summary_cn.md)

## 6.CPU特性用于性能分析 CPU-Features-For-Performance-Analysis
* [6-0.CPU特性用于性能分析](./chapters/6-CPU-Features-For-Performance-Analysis/6-0_Intro_cn.md)
* [6-1.自顶向下微架构分析 ](./chapters/6-CPU-Features-For-Performance-Analysis/6-1_Top-Down_Microarchitecture_Analysis_cn.md)
* [6-2.TMA在英特尔处理器上](./chapters/6-CPU-Features-For-Performance-Analysis/6-2_TMA-Intel_cn.md)
* [6-3.TMA在AMD处理器上](./chapters/6-CPU-Features-For-Performance-Analysis/6-3_TMA-AMD_cn.md)
* [6-4.TMA 在 ARM 处理器上](./chapters/6-CPU-Features-For-Performance-Analysis/6-4_TMA-ARM_cn.md)
* [6-5.TMA 总结](./chapters/6-CPU-Features-For-Performance-Analysis/6-5_TMA-summary_cn.md)
* [6-6.分支记录机制](./chapters/6-CPU-Features-For-Performance-Analysis/6-6_Last_Branch_Record_cn.md)
* [6-7.基于硬件的采样功能](./chapters/6-CPU-Features-For-Performance-Analysis/6-7_Precise_Event_Based_Sampling_PEBS_cn.md)
* [6-8.问题和练习](./chapters/6-CPU-Features-For-Performance-Analysis/6-8_Questions-Exercises_cn.md)
* [6-9.章节总结](./chapters/6-CPU-Features-For-Performance-Analysis/6-9_Chapter_Summary_cn.md)

## 7.性能分析工具概述 Overview-Of-Performance-Analysis-Tools
* [7-0.性能分析工具概述](./chapters/7-Overview-Of-Performance-Analysis-Tools/7-0_Introduction_cn.md)
* [7-1.Intel Vtune](./chapters/7-Overview-Of-Performance-Analysis-Tools/7-1_Intel_Vtune_cn.md)
* [7-2.AMD uProf](./chapters/7-Overview-Of-Performance-Analysis-Tools/7-2_AMD_uprof_cn.md)
* [7-3.Apple Xcode Instruments](./chapters/7-Overview-Of-Performance-Analysis-Tools/7-3_Apple_Instruments_cn.md)
* [7-4.Linux Perf](./chapters/7-Overview-Of-Performance-Analysis-Tools/7-4_Linux_perf_cn.md)
* [7-5.火焰图](./chapters/7-Overview-Of-Performance-Analysis-Tools/7-5_Flamegraphs_cn.md)
* [7-6.Windows 事件跟踪](./chapters/7-Overview-Of-Performance-Analysis-Tools/7-6_Windows_ETW_cn.md)
* [7-7.专业和混合性能分析器](./chapters/7-Overview-Of-Performance-Analysis-Tools/7-7_Tracy_cn.md)
* [7-8.持续性能分析](./chapters/7-Overview-Of-Performance-Analysis-Tools/7-8_Continuous_Profiling_cn.md)
* [7-9.问题和练习](./chapters/7-Overview-Of-Performance-Analysis-Tools/7-9_Questions-Exercises_cn.md)
* [7-10.章节总结](./chapters/7-Overview-Of-Performance-Analysis-Tools/7-10_Chapter_summary_cn.md)

## 8.优化内存访问 Optimizing-Memory-Accesses
* [8-0.源代码优化](./chapters/8-Optimizing-Memory-Accesses/8-0_Source_Code_Tuning_For_CPU_cn.md)
* [8-1.优化内存访问](./chapters/8-Optimizing-Memory-Accesses/8-1_Optimizing_Memory_Accesses_cn.md)
* [8-2.缓存友好数据结构](./chapters/8-Optimizing-Memory-Accesses/8-2_Cache-Friendly_Data_Structures_cn.md)
* [8-3.显式内存预取](./chapters/8-Optimizing-Memory-Accesses/8-3_Memory_Prefetching_cn.md)
* [8-3.内存分析](./chapters/8-Optimizing-Memory-Accesses/8-3_Memory_Profiling_cn.md)
* [8-4.减少 DTLB 未命中 ](./chapters/8-Optimizing-Memory-Accesses/8-4_Reducing_DTLB_misses_cn.md)
* [8-5.问题与练习](./chapters/8-Optimizing-Memory-Accesses/8-5_Questions-Exercises_cn.md)
* [8-6.章节总结](./chapters/8-Optimizing-Memory-Accesses/8-6_Chapter_Summary_cn.md)

## 9.优化计算 Optimizing-Computations
* [9-0.优化计算](./chapters/9-Optimizing-Computations/9-0_Core_Bound_cn.md)
* [9-1.数据流依赖](./chapters/9-Optimizing-Computations/9-1_Data_Dependencies_cn.md)
* [9-2.内联函数](./chapters/9-Optimizing-Computations/9-2_Inlining_Functions_cn.md)
* [9-3.循环优化](./chapters/9-Optimizing-Computations/9-3_Loop_Optimizations_cn.md)
* [9-4.向量化](./chapters/9-Optimizing-Computations/9-4_Vectorization_cn.md)
* [9-5.使用编译器内部函数](./chapters/9-Optimizing-Computations/9-5_Compiler_Intrinsics_cn.md)
* [9-6.问题和练习](./chapters/9-Optimizing-Computations/9-6_Questions-Exercises_cn.md)
* [9-7.章节总结](./chapters/9-Optimizing-Computations/9-7_Chapter_Summary_cn.md)

## 10.优化分支预测 Optimizing-Branch-Prediction
* [10-0.优化分支预测](./chapters/10-Optimizing-Branch-Prediction/10-0_Optimizing_bad_speculation_cn.md)
* [10-1.用查找表替换分支](./chapters/10-Optimizing-Branch-Prediction/10-0_Optimizing_bad_speculation_cn.md)
* [10-2.用算术替换分支](./chapters/10-Optimizing-Branch-Prediction/10-2_Replace_branches_with_arithmetic_cn.md)
* [10-3.用谓词替换分支](./chapters/10-Optimizing-Branch-Prediction/10-3_Replace_branches_with_predication_cn.md)
* [10-4.问题和练习](./chapters/10-Optimizing-Branch-Prediction/10-4_Questions-Exercises_cn.md)
* [10-5.章节总结](./chapters/10-Optimizing-Branch-Prediction/10-5_Chapter_Summary_cn.md)

## 11.机器代码布局优化 Machine-Code-Layout-Optimizations
* [11-1.机器代码布局优化](./chapters/11-Machine-Code-Layout-Optimizations/11-1_Machine_Code_Layout_cn.md)
* [11-2.基本块](./chapters/11-Machine-Code-Layout-Optimizations/11-2_Basic_Block_cn.md)
* [11-3.基本块布局](./chapters/11-Machine-Code-Layout-Optimizations/11-3_Basic_Block_Placement_cn.md)
* [11-4.基本块对齐](./chapters/11-Machine-Code-Layout-Optimizations/11-4_Basic_Block_Alignment_cn.md)
* [11-5.函数拆分](./chapters/11-Machine-Code-Layout-Optimizations/11-5_Function_Splitting_cn.md)
* [11-6.函数重排序](./chapters/11-Machine-Code-Layout-Optimizations/11-6_Function_Reordering_cn.md)
* [11-7.使用配置分析文件引导的优化](./chapters/11-Machine-Code-Layout-Optimizations/11-7_PGO_cn.md)
* [11-8.减少 ITLB 未命中](./chapters/11-Machine-Code-Layout-Optimizations/11-8_Reducing_ITLB_misses_cn.md)
* [11-9.案例研究：测量代码足迹](./chapters/11-Machine-Code-Layout-Optimizations/11-9_Code_footprint_cn.md)
* [11-10.问题和练习](./chapters/11-Machine-Code-Layout-Optimizations/11-10_Questions-Exercises_cn.md)
* [11-11.章节总结](./chapters/11-Machine-Code-Layout-Optimizations/11-11_Chapter_Summary_cn.md)

## 12.其他优化领域 Other-Tuning-Areas
* [12-0.其他优化领域](./chapters/12-Other-Tuning-Areas/12-0_Other_tuning_areas_cn.md)
* [12-1.优化输入输出](./chapters/12-Other-Tuning-Areas/12-1_Optimizing_Input-Output_cn.md)
* [12-3.架构特定优化(todo)](./chapters/12-Other-Tuning-Areas/12-3_Architecture-Specific_Optimizations_cn.md)
* [12-4.低延迟优化技术](./chapters/12-Other-Tuning-Areas/12-4_Low-Latency-Tuning-Techniques_cn.md)
* [12-5.缓慢的浮点运算](./chapters/12-Other-Tuning-Areas/12-5_Detecting_Slow_FP_Arithmetic_cn.md)
* [12-6.系统调优](./chapters/12-Other-Tuning-Areas/12-6_System_Tuning_cn.md)
* [12-7.案例研究：对最后一级缓存大小的敏感性](./chapters/12-Other-Tuning-Areas/12-7_Case_Study_-_LLC_sensitivity_cn.md)
* [12-8.问题和练习](./chapters/12-Other-Tuning-Areas/12-8_Questions-Exercises_cn.md)
* [12-9.章节总结](./chapters/12-Other-Tuning-Areas/12-9_Chapter_summary_cn.md)

## 13.优化多线程应用 Optimizing-Multithreaded-Applications
* [13-0.优化多线程应用](./chapters/13-Optimizing-Multithreaded-Applications/13-0_Optimizing_Multithreaded_Applications_cn.md)
* [13-1.性能扩展和开销](./chapters/13-Optimizing-Multithreaded-Applications/13-1_Performance_scaling_and_overhead_cn.md)
* [13-2.并行效率指标](./chapters/13-Optimizing-Multithreaded-Applications/13-2_Parallel_Efficiency_Metrics_cn.md)
* [13-3.使用 Intel VTune Profiler 进行分析](./chapters/13-Optimizing-Multithreaded-Applications/13-3_Analysis_With_Vtune_cn.md)
* [13-4.使用 Linux Perf 进行分析](./chapters/13-Optimizing-Multithreaded-Applications/13-4_Analysis_with_Linux_Perf_cn.md)
* [13-5.使用 Coz 进行分析](./chapters/13-Optimizing-Multithreaded-Applications/13-5_Analysis_with_Coz_cn.md)
* [13-6.利用 eBPF 和 GAPP 进行分析](./chapters/13-Optimizing-Multithreaded-Applications/13-6_Analysis_with_eBPF_and_GAPP_cn.md)
* [13-7.缓存一致性问题](./chapters/13-Optimizing-Multithreaded-Applications/13-7_Cache_Coherence_Issues_cn.md)
* [13-8.问题和练习](./chapters/13-Optimizing-Multithreaded-Applications/13-8_Questions-Exercises_cn.md)
* [13-9.章节总结](./chapters/13-Optimizing-Multithreaded-Applications/13-9_Chapter_Summary_cn.md)

## 14.软件和硬件性能的当前和未来趋势 Current-And-Future-Trends
* [14-0.软件和硬件性能的当前和未来趋势](./chapters/14-Current-And-Future-Trends/14-0_Introduction_cn.md)

## 15.后记 Epilog
* [15-0.后记](./chapters/15-Epilog/15-0_Epilog_cn.md)

## 16.术语表 Glossary
* [16-0.术语表](./chapters/16-Glossary/16-0_Glossary_cn.md)

## 17.主要CPU微架构列表 List-of-Uarch-ISA
* [17-0.主要CPU微架构列表](./chapters/17-List-of-Uarch-ISA/17-0_List_of_uarchs_cn.md)


## 18.附录 Appendix
----
* [附录 A](./chapters/18-Appendix/Appendix-A_cn.md)
* [附录 B](./chapters/18-Appendix/Appendix-B_cn.md)
* [附录 C](./chapters/18-Appendix/Appendix-C_cn.md)
* [附录 D](./chapters/18-Appendix/Appendix-D_cn.md)

----
## 引用
* [References](./chapters/References.md)

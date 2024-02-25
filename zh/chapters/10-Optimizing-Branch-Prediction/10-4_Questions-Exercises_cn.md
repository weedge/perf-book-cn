## 问题和练习 {.unlisted .unnumbered}

1. 使用本章讨论的技术解决以下实验作业：
    - `perf-ninja::branches_to_cmov_1`
    - `perf-ninja::lookup_tables_1`
    - `perf-ninja::virtual_call_mispredict`
    - `perf-ninja::conditional_store_1`
2. 运行您每天使用的应用程序。收集 TMA 细分并检查 `BadSpeculation` 指标。查看代码中哪个部分归因于最多的分支预测错误。是否可以使用本章讨论的技术来避免分支？

**编码练习**：编写一个微基准，使其经历 50% 的预测错误率或尽可能接近 50%。您的目标是用代码编写，使其所有分支指令中有一半被预测错误。这并不像您想象的那么简单。一些提示和想法：
   - 分支预测错误率计算为 `BR_MISP_RETIRED.ALL_BRANCHES / BR_INST_RETIRED.ALL_BRANCHES`。
   - 如果使用 C++ 编码，您可以 1) 使用类似于 perf-ninja 的 google benchmark，或 2) 编写常规控制台程序并使用 Linux `perf` 收集 CPU 计数器，或 3) 将 libpfm 集成到微基准中（参见 [@sec:MarkerAPI])。
   - 无需发明复杂的算法。一种简单的方法是在范围 `[0;100)` 中生成一个伪随机数，并检查它是否小于 50。随机数可以提前预生成。
   - 请记住，现代 CPU 可以记住较长（但仍然有限）的分支结果序列。


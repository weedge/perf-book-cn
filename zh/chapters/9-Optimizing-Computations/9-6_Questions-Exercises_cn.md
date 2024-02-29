## 问题和练习 

1. 使用本章讨论的技术解决以下实验作业：
    - `perf-ninja::function_inlining_1` 
    - `perf-ninja::vectorization` 1 & 2
    - `perf-ninja::dep_chains` 1 & 2
    - `perf-ninja::compiler_intrinsics` 1 & 2
    - `perf-ninja::loop_interchange` 1 & 2
    - `perf-ninja::loop_tiling_1`
2. 描述您将采取哪些步骤来找出应用程序是否利用了所有利用 SIMD 代码的机会？
3. 尝试在实际代码上手动进行循环优化（但不要提交）。确保所有测试仍然通过。
4. 假设您正在处理一个 IpCall（每次调用指令）指标非常低的应用程序。您将尝试应用/强制哪些优化？
5. 每天运行您正在使用的应用程序。找到程序中最热的循环。它是矢量化的吗？可以强制编译器自动矢量化吗？附加问题：循环是由依赖链还是执行吞吐量导致瓶颈？

### TMA 在 AMD 处理器上 {#sec:secTMA_AMD}

[TODO]: TMA 从哪个内核版本开始在 Linux perf 中支持？

从 Zen4 开始，AMD 处理器支持一级和二级 TMA 分析。根据 AMD 文档，它被称为“管道利用率”分析，但基本思想保持不变。L1 和 L2 桶也与 Intel 的非常相似。Linux 用户可以使用 `perf` 工具收集管道利用率数据。

接下来，我们将研究 Crypto++: [https://github.com/weidai11/cryptopp](https://github.com/weidai11/cryptopp)[^1] 实现的 SHA-256（安全散列算法 256），它是比特币挖掘的基本密码算法。Crypto++ 是一个开源的 C++ 密码算法类库，包含许多算法的实现，不仅仅是 SHA-256。但是，对于我们的示例，我们通过注释掉 `bench1.cpp` 中 `BenchmarkUnkeyedAlgorithms` 函数中相应的行来禁用所有其他算法的基准测试。

我们在配备 Ubuntu 22.04、Linux 内核 6.5.0-15-generic 的 AMD Ryzen 9 7950X 机器上运行了测试。我们使用 GCC 12.3 C++ 编译器编译了 Crypto++ 版本 8.9。我们使用了默认的 `-O3` 优化选项，但由于代码是用 x86 内在函数编写的（请参阅 [@sec:secIntrinsics]）并利用了 SHA x86 ISA 扩展，因此对性能影响不大。

下面是我们用来获取 L1 和 L2 管道利用率指标的命令。输出经过修剪，删除了一些统计数据以消除不必要的干扰。

```bash
$ perf stat -M PipelineL1,PipelineL2 -- ./cryptest.exe b1 10
 0.0 %  bad_speculation_mispredicts        (20.08%) 
 0.0 %  bad_speculation_pipeline_restarts  (20.08%)
 0.0 %  bad_speculation                    (20.08%)
 6.1 %  frontend_bound                     (20.00%)
 6.1 %  frontend_bound_bandwidth           (20.00%)
 0.1 %  frontend_bound_latency             (20.00%)
65.9 %  backend_bound_cpu                  (20.00%)
 1.7 %  backend_bound_memory               (20.00%)
67.5 %  backend_bound                      (20.00%)
26.3 %  retiring                           (20.08%)
20.2 %  retiring_fastpath                  (19.99%)
 6.1 %  retiring_microcode                 (19.99%)
```

在输出中，括号中的数字表示运行时持续时间的百分比，当时正在监控指标。正如我们看到的，由于多路复用，所有指标只被监控了 20% 的时间。在我们的案例中，这可能不是问题，因为 SHA256 具有一致的行为，但并非总是如此。为了最小化多路复用的影响，您可以在单个运行中收集一组有限的指标，例如 `perf stat -M frontend_bound,backend_bound`。

上面显示的管道利用率指标的描述可以在 [@AMDUprofManual, 第 2.8 章 管道利用率] 中找到。通过查看这些指标，我们可以看到分支预测不会在 SHA256 中发生（`bad_speculation` 为 0%）。仅使用了可用调度槽位的 26.3%（`retiring`），这意味着其余 73.7% 由于前端和后端停顿而浪费。

加密指令并非简单，因此在内部被分解成更小的片段（μops）。一旦处理器遇到这样的指令，它就会从微码中检索它的 μops。微操作是从微码排序器获取的，带宽低于常规指令解码器，使其成为性能瓶颈的潜在来源。Crypto++ SHA256 实现大量使用诸如 `SHA256MSG2`, `SHA256RNDS2` 等指令，这些指令根据 uops.info: [https://uops.info/table.html](https://uops.info/table.html)[^2] 网站由多个 μops 组成。`retiring_microcode` 指标表明 6.1% 的调度槽位被微码操作使用。由于前端的带宽瓶颈，相同数量的调度槽位未使用（`frontend_bound_bandwidth`）。这两个指标共同表明，这 6.1% 的调度槽位被浪费，因为微码排序器没有提供 μops，而后端本可以消耗它们。

[TODO]: 为什么 `frontend_bound_bandwidth` 和 `retiring_microcode` 都有 6.1%？这些指标之间存在特定关系吗？我在文本中描述得正确吗？

大多数周期都停滞在 CPU 后端（`backend_bound`），但只有 1.7% 的周期由于等待内存访问而停滞（`backend_bound_memory`）。因此，我们知道基准测试主要受机器的计算能力限制。正如您将在本书第二部分中了解到的，这可能与数据流依赖性或某些加密操作的执行吞吐量有关。它们比传统的 `ADD`, `SUB`, `CMP` 等指令不那么频繁，因此通常只能在单个执行单元上执行。大量这样的操作可能会使该特定单元的执行吞吐量饱和。进一步的分析应该更仔细地观察源代码和生成的汇编代码，检查执行端口利用率，查找数据依赖性等；我们将在此停止。

就 Windows 而言，在撰写本文时，TMA 方法仅在服务器平台（代号 Genoa）上受支持，而不支持客户端系统（代号 Raphael）。TMA 支持在 AMD uProf 版本 4.1 中添加，但仅在命令行工具 `AMDuProfPcm` 工具中，它是 AMD uProf 安装的一部分。您可以参考 [@AMDUprofManual, 第 2.8 章 管道利用率] 了解更多有关如何运行分析的详细信息。AMD uProf 的图形版本还没有 TMA 分析。 

[TODO]: AMDuProfPcm 的 4.2 版本是否适用于客户端部分？

[^1]: Crypto++ - [https://github.com/weidai11/cryptopp](https://github.com/weidai11/cryptopp)
[^2]: uops.info - [https://uops.info/table.html](https://uops.info/table.html)

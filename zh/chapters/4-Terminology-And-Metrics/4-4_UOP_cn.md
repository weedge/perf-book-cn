---
typora-root-url: ..\..\img
---

## 微操作 {#sec:sec_UOP}

具有 x86 架构的微处理器将复杂的 CISC 类指令转换为简单的 RISC 类微操作，缩写为 $\mu$ops 或 $\mu$ops。例如，像 `ADD rax, rbx` 这样的简单加法指令只会生成一个 $\mu$op，而更复杂的指令比如 `ADD rax, [mem]` 可能生成两个：一个用于从 `mem` 内存位置读取到临时（未命名）寄存器，另一个用于将其添加到 `rax` 寄存器。指令 `ADD [mem], rax` 会生成三个 $\mu$ops：一个用于从内存读取，一个用于相加，一个用于将结果写回内存。

将指令分割成微操作的主要优点是 $\mu$ops 可以执行：

* **乱序**: 考虑 `PUSH rbx` 指令，它将栈指针减少 8 字节，然后将源操作数存储在栈顶。假设在解码后 `PUSH rbx` 被“破解”成两个依赖的微操作：

```
SUB rsp, 8
STORE [rsp], rbx
```

通常，函数序言通过使用多个 `PUSH` 指令保存多个寄存器。在我们的例子中，下一个 `PUSH` 指令可以在前一个 `PUSH` 指令的 `SUB` $\mu$op 完成后开始执行，而不必等待现在可以异步执行的 `STORE` $\mu$op。

* **并行**: 考虑 `HADDPD xmm1, xmm2` 指令，它将在 `xmm1` 和 `xmm2` 中对两个双精度浮点数进行求和（减少），并将两个结果存储在 `xmm1` 中，如下所示：

```
xmm1[63:0] = xmm2[127:64] + xmm2[63:0]
xmm1[127:64] = xmm1[127:64] + xmm1[63:0]
```

微代码化此指令的一种方法是执行以下操作：1) 减少 `xmm2`并将结果存储在 `xmm_tmp1[63:0]` 中，2) 减少 `xmm1`并将结果存储在 `xmm_tmp2[63:0]` 中，3) 将 `xmm_tmp1` 和 `xmm_tmp2` 合并到 `xmm1` 中。总共三个 $\mu$ops。请注意，步骤 1) 和 2) 是独立的，因此可以并行完成。

尽管我们刚刚讨论了如何将指令分割成更小的部分，但有时 $\mu$ops 也可以融合在一起。现代 CPU 中有两种类型的融合：

* **微融合**: 融合来自同一机器指令的 $\mu$ops。微融合只能应用于两种类型的组合：内存写操作和读改操作。例如：

```bash
add eax, [mem]
```

这条指令中有两个 $\mu$ops：1) 读取内存位置 `mem`，2) 将其添加到 `eax`。使用微融合，在解码步骤中将两个 $\mu$ops 融合成一个。

* **宏融合**: 融合来自不同机器指令的 $\mu$ops。在某些情况下，解码器可以将算术或逻辑指令与 subsequent 条件跳转指令融合成单个计算和分支 $\mu$op。例如：

```bash
.loop:
  dec rdi
  jnz .loop
```

使用宏融合，将来自 `DEC` 和 `JNZ` 指令的两个 $\mu$ops 融合成一个。

微融合和宏融合都可以节省从解码到退休的所有管道阶段的带宽。融合操作在重新排序缓冲区 (ROB) 中共享单个条目。当一个融合的 $\mu$op 只使用一个条目时，ROB 的容量得到更好的利用。这样的一个融合的 ROB 条目稍后会分派到两个不同的执行端口，但作为单个单元再次退休。读者可以 [@fogMicroarchitecture] 中了解更多关于 $\mu$op 融合的信息。

要收集应用程序发出的、执行的和退休的 $\mu$ops 数量，您可以使用 Linux `perf`，如下所示：

```bash
$ perf stat -e uops_issued.any,uops_executed.thread,uops_retired.slots -- ./a.exe
2856278 uops_issued.any
2720241 uops_executed.thread
2557884 uops_retired.slots
```

指令被分解成微操作的方式可能会随着 CPU 世代的不同而有所差异。通常，用于一条指令的 $\mu$ops 数量越少，意味着硬件对其支持越好，并且可能具有更低的延迟和更高的吞吐量。对于最新的 Intel 和 AMD CPU，绝大多数指令都会生成恰好一个 $\mu$op。有关最近微架构中 x86 指令的延迟、吞吐量、端口使用情况和 $\mu$ops 数量，可以参考 uops.info: [https://uops.info/table.html](https://uops.info/table.html)[^1] 网站。

[^1]: 指令延迟和吞吐量 - [https://uops.info/table.html](https://uops.info/table.html)

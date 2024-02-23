## 分支记录机制（Branch Recording Mechanisms） {#sec:lbr}

现代高性能 CPU 提供分支记录机制，使处理器能够连续记录一组先前执行的分支。但在进入细节之前，你可能会问：*为什么我们对分支如此感兴趣？* 嗯，因为这是我们如何确定程序控制流的方式。我们基本上忽略基本块（参见 [@sec:BasicBlock]）中的其他指令，因为分支总是基本块中的最后一个指令。由于基本块中的所有指令都保证执行一次，因此我们只能关注将“代表”整个基本块的分支。因此，如果我们跟踪每个分支的结果，就可以重建程序的整个逐行执行路径。事实上，这就是英特尔处理器跟踪 (PT) 功能可以做到的，它在附录 D 中讨论。我们将在这里讨论的分支记录机制基于采样而不是跟踪，因此具有不同的用例和功能。

由英特尔、AMD 和 ARM 设计的处理器都宣布了他们的分支记录扩展。确切的实现可能会有所不同，但基本思想是相同的。硬件并行记录每个分支的“来自”和“到”地址以及一些额外数据，同时执行程序。如果我们收集足够长的源目的地对历史记录，我们将能够像调用堆栈一样解开程序的控制流，但深度有限。此类扩展旨在使正在运行的程序的运行速度降低到最小，通常在 1% 以内。

如果使用分支记录机制，我们可以在分支（或周期，没关系）上进行采样，但在每个采样期间，查看先前执行的 N 个分支。这使我们在热门代码路径中合理地覆盖了控制流，但不会让我们因为只检查了总数较少的分支而获得过多信息。请务必记住，这仍然是采样，因此并不是每个执行的分支都可以被检查。CPU 通常执行得太快，无法做到这一点。

非常重要的一点是，只记录已采取的分支。[@lst:LogBranches] 显示了如何跟踪分支结果的示例。此代码表示一个循环，其中三个指令可能会改变程序的执行路径，即循环后缘 `JNE` (1)、条件分支 `JNS` (2)、函数 `CALL` (3) 和从此函数返回 (4，未显示)。

代码清单：记录分支的示例。

~~~~ {#lst:LogBranches .asm}
----> 4eda10:  mov   edi,DWORD PTR [rbx]
|     4eda12:  test  edi,edi
| --- 4eda14:  jns   4eda1e              <== (2)
| |   4eda16:  mov   eax,edi
| |   4eda18:  shl   eax,0x7
| |   4eda1b:  lea   edi,[rax+rdi*8]
| └─> 4eda1e:  call  4edb26              <== (3)
|     4eda23:  add   rbx,0x4             <== (4)
|     4eda27:  mov   DWORD PTR [rbx-0x4],eax
|     4eda2a:  cmp   rbx,rbp
 ---- 4eda2d:  jne   4eda10              <== (1)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

以下是使用分支记录机制可以记录的可能分支历史之一。它显示了执行 `CALL` 指令时最近的 7 个分支结果（未显示更多）。由于在循环的最新迭代中没有执行 `JNS` 分支 (`4eda14` -> `4eda1e`)，因此它没有被记录，因此不会出现在历史记录中。

```
    Source Address    Destination Address
    ...               ...
(1) 4eda2d            4eda10    <== next iteration
(2) 4eda14            4eda1e    <== jns taken
(3) 4eda1e            4edb26    <== call a function
(4) 4b01cd            4eda23    <== return from a function
(1) 4eda2d            4eda10    <== next iteration
(3) 4eda1e            4edb26    <== latest branch
```
## 未记录未执行的分支

未记录未执行的分支可能会增加分析负担，但通常不会使其过于复杂。由于我们知道控制流从条目 N-1 的目标地址到条目 N 的源地址是顺序的，因此我们仍然可以推断完整的执行路径。

接下来，我们将分别看一下每个供应商的分支记录机制，然后探讨如何在性能分析中使用它们。

### 英特尔平台上的 LBR

英特尔首次在其 Netburst 微架构中实现了其最后分支记录 (LBR) 功能。最初，它只能记录最近的 4 个分支结果。从 Nehalem 开始增加到 16，从 Skylake 开始增加到 32。在 Goldencove 微架构之前，LBR 被作为一组特定于模型的寄存器 (MSR) 实现，但现在它在架构寄存器内工作。其主要优点是 LBR 功能清晰可见，无需检查当前 CPU 的确切型号。这使操作系统和分析工具中的支持更加容易。此外，LBR 条目可以配置为包含在 PEBS 记录中（参见 [@sec:secPEBS]）。

LBR 寄存器就像一个不断被覆盖的环形缓冲区，仅提供最近的 32 个分支结果。每个 LBR 条目由三个 64 位值组成：

- 分支的源地址（“来自 IP”）。
- 分支的目标地址（“到 IP”）。
- 操作的元数据，包括错误预测和经过周期时间信息。

除了源地址和目标地址之外，保存的其他信息还有一些重要的应用，我们将在稍后讨论。

当采样计数器溢出并触发性能监控中断 (PMI) 时，LBR 记录冻结，直到软件捕获 LBR 记录并恢复收集。

LBR 收集可以限制在一组特定的分支类型上，例如用户可以选择只记录函数调用和返回。将此类过滤器应用于 [@lst:LogBranches] 中的代码，我们只会看到历史记录中的分支 (3) 和 (4)。用户还可以过滤进/出条件跳转和无条件跳转、间接跳转和调用、系统调用、中断等。在 Linux perf 中，有一个 `-j` 选项可以启用/禁用记录各种分支类型。

默认情况下，LBR 数组作为一个环形缓冲区，捕获控制流转换。然而，LBR 数组的深度是有限的，这在分析某些应用程序时可能是一个限制因素，其中执行流的转换伴随着大量叶函数调用。这些对叶函数的调用及其返回很可能会将主执行上下文从 LBR 中移除。再次考虑 [@lst:LogBranches] 中的示例。假设我们想要从 LBR 中的历史记录中解开调用堆栈，因此我们将 LBR 配置为仅捕获函数调用和返回。如果循环运行数千次迭代，并且考虑到 LBR 数组只有 32 个条目，那么我们只看到 16 对条目 (3) 和 (4) 的可能性非常高。在这种情况下，LBR 数组充满了叶函数调用，这些调用对我们解开当前调用堆栈没有帮助。

这就是为什么 LBR 支持调用堆栈模式。启用此模式后，LBR 数组仍像以前一样捕获函数调用，但随着返回指令的执行，最后捕获的分支 (`call`) 记录将以后进先出 (LIFO) 方式从数组中刷新。因此，与已完成叶函数相关的分支信息将不会保留，同时保留主执行路径的调用堆栈信息。使用这种配置，LBR 数组模拟一个调用堆栈，其中 `CALL` 会将条目“压入”堆栈，而 `RET` 则会将条目“弹出”堆栈。如果你的应用程序中调用堆栈的深度永远不会超过 32 个嵌套框架，LBR 将为你提供非常准确的信息。[@IntelOptimizationManual，第 3B 卷，第 19 章 最后分支记录]

可以使用以下命令确保你的系统上的 LBR 已启用：

```bash
$ dmesg | grep -i lbr
[    0.228149] Performance Events: PEBS fmt3+, 32-deep LBR, Skylake events, full-width counters, Intel PMU driver.
```

使用Linux的`perf`，可以使用以下命令收集LBR堆栈:

```bash
$ perf record -b -e cycles ./benchmark.exe
[ perf record: Woken up 68 times to write data ]
[ perf record: Captured and wrote 17.205 MB perf.data (22089 samples) ]
```

LBR 堆栈也可以使用 `perf record --call-graph lbr` 命令收集，但是收集的信息量少于使用 `perf record -b`。例如，在运行 `perf record --call-graph lbr` 时不会收集分支预测和周期数据。

因为每个收集的样本都捕获整个 LBR 堆栈（32 个最后的分支记录），所以收集的数据（`perf.data`）的大小比不使用 LBR 的采样要大得多。尽管如此，在大多数 LBR 使用案例中，运行时开销低于 1%。[@Nowak2014TheOO]

用户可以导出原始 LBR 堆栈进行自定义分析。以下是可以用来转储收集的分支堆栈内容的 Linux perf 命令：

```bash
$ perf record -b -e cycles ./benchmark.exe
$ perf script -F brstack &> dump.txt
```

`dump.txt`文件可能非常大，包含如下所示的行:

```
...
0x4edaf9/0x4edab0/P/-/-/29   
0x4edabd/0x4edad0/P/-/-/2
0x4edadd/0x4edb00/M/-/-/4
0x4edb24/0x4edab0/P/-/-/24
0x4edabd/0x4edad0/P/-/-/2
0x4edadd/0x4edb00/M/-/-/1
0x4edb24/0x4edab0/P/-/-/3
0x4edabd/0x4edad0/P/-/-/1
...
```

上述输出展示了 LBR 堆栈中的 8 个条目，LBR 堆栈通常包含 32 个条目。每个条目都有 `FROM` 和 `TO` 地址（十六进制值）、预测标志 (`M` - 预测错误，`P` - 预测正确）以及周期数（每个条目最后一个位置的数字）。用“`-`”标记的组件与事务内存扩展 (TSX) 相关，我们将在本文中不进行讨论。好奇的读者可以参考 `perf script` 规范: [http://man7.org/linux/man-pages/man1/perf-script.1.html](http://man7.org/linux/man-pages/man1/perf-script.1.html)[^2] 中解码的 LBR 条目的格式。

### AMD 平台上的 LBR

AMD 处理器也支持 AMD Zen4 处理器上的最后分支记录 (LBR)。Zen4 拥有 16 对“from”和“to”地址日志以及一些额外的元数据。类似于 Intel LBR，AMD 处理器能够记录各种类型的分支。与 Intel LBR 的主要区别在于 AMD 处理器目前还不支持调用堆栈模式，因此 LBR 功能无法用于调用堆栈收集。另一个明显的区别是 AMD LBR 记录中没有周期计数字段。有关更多详细信息，请参见 [@AMDProgrammingManual，13.1.1.9 最后分支堆栈寄存器]。

从 Linux 内核 6.1 开始，Linux “perf” 在 AMD Zen4 处理器上支持我们将在下面讨论的分支分析用例，除非另有明确说明。Linux `perf` 命令收集 AMD LBR 使用相同的 `-b` 和 `-j` 选项。

使用 AMD uProf CLI 工具也可以进行分支分析。以下示例命令将转储收集的原始 LBR 记录并生成 CSV 报告：

```bash
$ AMDuProfCLI collect --branch-filter -o /tmp/ ./AMDTClassicMatMul-bin
```

## ARM 平台上的 BRBE

ARM 在 2020 年作为 ARMv9.2-A ISA 的一部分推出了其名为 BRBE 的分支记录扩展。ARM BRBE 与英特尔的 LBR 非常相似，提供了许多类似的功能。就像英特尔的 LBR 一样，BRBE 记录也包含源地址和目标地址、预测错误位和周期计数值。根据最新可用的 BRBE 规范，不支持调用堆栈模式。分支记录仅包含已在架构上执行的分支的信息，即不在预测错误路径上。用户还可以根据特定分支类型过滤记录。一个值得注意的区别是 BRBE 支持可配置的 BRBE 缓冲区深度：处理器可以选择 BRBE 缓冲区的容量为 8、16、32 或 64 个记录。更多细节可在 [@Armv9ManualSupplement, 章节 F1 "Branch Record Buffer Extension"] 中找到。

在撰写本文时，还没有商用机器实现 ARMv9.2-A，因此无法测试此扩展的实际运行情况。

### 捕获调用堆栈

分支记录使许多重要用例成为可能。在本节和接下来的几节中，我们将介绍最重要的几个用例。

分支记录最流行的用例之一是捕获调用堆栈。我们已经在 [@sec:secCollectCallStacks] 中介绍了为什么需要收集它们。即使你编译了一个没有帧指针或调试信息的程序，分支记录也可以用作收集调用图信息的轻量级替代方法。

在撰写本文时 (2023 年)，AMD 的 LBR 和 ARM 的 BRBE 不支持调用堆栈收集，但英特尔的 LBR 支持。以下是你可以使用英特尔 LBR 执行此操作的方法：

```bash
$ perf record --call-graph lbr -- ./a.exe
$ perf report -n --stdio
# Children   Self    Samples  Command  Object  Symbol       
# ........  .......  .......  .......  ......  .......
	99.96%  99.94%    65447    a.exe    a.exe  [.] bar
            |          
             --99.94%--main
                       |          
                       |--90.86%--foo
                       |          |          
                       |           --90.86%--bar
                       |          
                        --9.08%--zoo
                                  bar
```

正如你所见，我们已经确定了程序中最热的功能（即 `bar`）。我们还发现调用者对函数 `bar` 中花费的大部分时间做出了贡献：该工具捕获了 `main->foo->bar` 调用堆栈 91% 的时间，捕获了 `main->zoo->bar` 9% 的时间。换句话说，`bar` 中 91% 的样本都将 `foo` 作为其调用者函数。

值得一提的是，在这种情况下，我们不一定能得出关于函数调用次数的结论。例如，我们不能说 `foo` 调用 `bar` 的频率比 `zoo` 高 10 倍。可能的情况是，`foo` 调用 `bar` 一次，但在 `bar` 内部执行了昂贵的路径，而 `zoo` 调用 `bar` 多次，但很快就返回。

### 识别热点分支（#sec:lbr_hot_branch）

分支记录还使我们能够知道哪些分支被采取的频率最高。它在 Intel 和 AMD 上都支持。根据 ARM 的 BRBE 规范，它可以支持，但由于缺乏实现此扩展的处理器，无法验证。这里是一个例子：

[TODO]：检查：“添加 `-F +srcline_from,srcline_to` 会降低构建报告的速度。希望在更高版本的 perf 中，解码时间会得到改善”。

```bash
$ perf record -e cycles -b -- ./a.exe
[ perf record: Woken up 3 times to write data ]
[ perf record: Captured and wrote 0.535 MB perf.data (670 samples) ]
$ perf report -n --sort overhead,srcline_from,srcline_to -F +dso,symbol_from,symbol_to --stdio
# Samples: 21K of event 'cycles'
# Event count (approx.): 21440
# Overhead  Samples  Object  Source Sym  Target Sym  From Line  To Line
# ........  .......  ......  ..........  ..........  .........  .......
  51.65%      11074   a.exe   [.] bar    [.] bar      a.c:4      a.c:5
  22.30%       4782   a.exe   [.] foo    [.] bar      a.c:10     (null)
  21.89%       4693   a.exe   [.] foo    [.] zoo      a.c:11     (null)
   4.03%        863   a.exe   [.] main   [.] foo      a.c:21     (null)
```

从这个例子中，我们可以看到超过 50% 的已采取分支位于 `bar` 函数内，22% 的分支是来自 `foo` 到 `bar` 的函数调用，等等。请注意，`perf` 如何从 `cycles` 事件切换到分析 LBR 堆栈：只收集了 670 个样本，但每个样本都捕获了整个 LBR 堆栈。这为我们提供了 21440 个 LBR 条目（分支结果）进行分析。[^5]

大多数情况下，仅从代码行和目标符号就可以确定分支的位置。然而，理论上，可以编写代码，在单行上写两个 `if` 语句。此外，展开宏定义时，所有展开的代码都归于相同的源行，这也是可能发生此类情况的另一个场景。这个问题不会完全阻止分析，只会使其稍微困难一些。为了消除两个分支的歧义，您可能需要自己分析原始 LBR 堆栈（请参阅 easyperf 博客上的示例：[https://easyperf.net/blog/2019/05/06/Estimating-branch-probability](https://easyperf.net/blog/2019/05/06/Estimating-branch-probability)[^6]）。

使用分支记录，我们还可以找到一个“超块”（有时称为“超级块”），它是函数中一系列热门基本块的链，这些基本块不一定按照顺序排列，但它们是顺序执行的。因此，超块代表了函数、代码片段或程序的典型热路径。

### 分析分支预测错误率（#sec:secLBR_misp_rate）

由于每个记录中保存的附加信息中包含预测错误位，因此还可以知道热门分支的预测错误率。在这个例子中，我们使用了 LLVM 测试套件中 7-zip 基准的纯 C 代码版本。[^7] `perf report` 的输出经过稍微修剪，以便更好地适应页面。以下用例在 Intel 和 AMD 上都支持。根据 ARM 的 BRBE 规范，它可以支持，但由于缺乏实现此扩展的处理器，无法验证。

```bash
$ perf record -e cycles -b -- ./7zip.exe b
$ perf report -n --sort symbol_from,symbol_to -F +mispredict,srcline_from,srcline_to --stdio
# Samples: 657K of event 'cycles'
# Event count (approx.): 657888
# Overhead  Samples  Mis  From Line  To Line  Source Sym  Target Sym
# ........  .......  ...  .........  .......  ..........  ..........
    46.12%   303391   N   dec.c:36   dec.c:40  LzmaDec     LzmaDec   
    22.33%   146900   N   enc.c:25   enc.c:26  LzmaFind    LzmaFind  
     6.70%    44074   N   lz.c:13    lz.c:27   LzmaEnc     LzmaEnc   
     6.33%    41665   Y   dec.c:36   dec.c:40  LzmaDec     LzmaDec 
```

在这个例子中，与函数 `LzmaDec` 相对应的行是我们特别关注的。按照上一节类似的分析，我们可以得出结论，`dec.c:36` 源行上的分支是基准测试中执行次数最多的分支。在 Linux `perf` 提供的输出中，我们可以看到两个与 `LzmaDec` 函数相对应的条目：一个带有 `Y` 字母，另一个带有 `N` 字母。将这两个条目一起分析，我们可以得到该分支的预测错误率。在这种情况下，我们知道 `dec.c:36` 行上的分支被正确预测了 `303391` 次（对应于 `N`），被错误预测了 `41665` 次（对应于 `Y`），因此预测率为 `88%`。

Linux `perf` 通过分析每个 LBR 条目并从中提取预测错误位来计算预测错误率。因此，对于每个分支，我们都知道它被正确预测的次数和错误预测的次数。同样，由于采样的性质，一些分支可能有一个 `N` 条目，但没有对应的 `Y` 条目。这可能意味着没有该分支被错误预测的 LBR 条目，但这并不意味着预测率是 `100%`。

### 机器码的精确计时（#sec:timed_lbr）

正如我们在英特尔 LBR 部分所展示的，从 Skylake 微架构开始，LBR 条目中有一个特殊的 `周期计数` 字段。这个附加字段指定了两个已采取分支之间经过的周期数。由于前一个 (N-1) LBR 条目中的目标地址是一个基本块 (BB) 的开始，而当前 (N) LBR 条目中的源地址是同一个基本块的最后一个指令，因此周期计数就是这个基本块的延迟。

这种类型的分析在 AMD 平台上不受支持，因为它们不会在 LBR 记录中记录周期计数。根据 ARM 的 BRBE 规范，它可以支持，但由于缺乏实现此扩展的处理器，无法验证。但是，英特尔支持它。这里是一个例子：

```
400618:   movb  $0x0, (%rbp,%rdx,1)    <= start of a BB
40061d:   add $0x1, %rdx 
400621:   cmp $0xc800000, %rdx 
400628:   jnz 0x400644                 <= end of a BB
```

假设我们在 LBR 堆栈中有两个条目：

```
  FROM_IP   TO_IP    Cycle Count
  ...       ...      ...
  40060a    400618    10
  400628    400644     5          <== LBR TOS
```

根据这些信息，我们知道从偏移量 `400618` 开始执行的基本块以 5 个周期执行了一次。如果我们收集足够多的样本，我们可以绘制该基本块延迟的概率密度图。

图 @fig:LBR_timing_BB 展示了这样的图表示例。它是通过分析所有满足上述规则的 LBR 条目编译而成的。读取图表的方法如下：它告诉我们给定延迟值出现的比率。例如，大约 2% 的时间测量到基本块延迟正好为 100 周期，14% 的时间测量到 280 周期，我们从未见过 150 到 200 周期之间的数值。另一种解读方式是：根据收集的数据，如果您要测量某个基本块的延迟，看到特定延迟的概率是多少？

![基本块延迟的概率密度图，基本块起始地址为 `0x400618`](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/pmu-features/LBR_timing_BB.png){#fig:LBR_timing_BB width=90%}

我们可以清楚地看到两个峰值：一个较小的峰值大约在 80 周期\circled{1}，两个更大的峰值在 280 和 305 周期\circled{2}。该块从一个不适合 CPU L3 缓存的大数组中进行非顺序加载，因此基本块的延迟很大程度上取决于此加载。基于图表，我们可以得出结论，第一个峰值\circled{1}对应于 L3 缓存命中，第二个峰值\circled{2}对应于 L3 缓存未命中，其中加载请求一直到主内存。

这些信息可以用于对该基本块进行细粒度调整。此示例可能受益于内存预取，我们将在 [@sec:memPrefetch] 中讨论。此外，周期计数信息可用于循环迭代的计时，其中每个循环迭代都以一个已采取的分支（后向边缘）结束。

在适当的性能分析工具支持到位之前，构建类似于图 @fig:LBR_timing_BB 的概率密度图需要手动解析原始 LBR 转储。有关如何执行此操作的示例，请参见 easyperf 博客: [https://easyperf.net/blog/2019/04/03/Precise-timing-of-machine-code-with-Linux-perf](https://easyperf.net/blog/2019/04/03/Precise-timing-of-machine-code-with-Linux-perf)[^9]。幸运的是，在较新的 Linux perf 版本中，获取这些信息要容易得多。以下示例直接使用 Linux perf 在我们之前介绍的 LLVM 测试套件中相同的 7-zip 基准测试上演示了这种方法：

[TODO]: 检查：“添加 `-F +srcline_from,srcline_to` 会降低构建报告的速度。希望在更高版本的 perf 中，解码时间会得到改善”。

```bash
$ perf record -e cycles -b -- ./7zip.exe b
$ perf report -n --sort symbol_from,symbol_to -F +cycles,srcline_from,srcline_to --stdio
# Samples: 658K of event 'cycles'
# Event count (approx.): 658240
# Overhead  Samples  BBCycles  FromSrcLine  ToSrcLine   
# ........  .......  ........  ...........  ..........  
     2.82%   18581      1      dec.c:325    dec.c:326   
     2.54%   16728      2      dec.c:174    dec.c:174   
     2.40%   15815      4      dec.c:174    dec.c:174   
     2.28%   15032      2      find.c:375   find.c:376  
     1.59%   10484      1      dec.c:174    dec.c:174   
     1.44%   9474       1      enc.c:1310   enc.c:1315  
     1.43%   9392      10      7zCrc.c:15   7zCrc.c:17  
     0.85%   5567      32      dec.c:174    dec.c:174   
     0.78%   5126       1      enc.c:820    find.c:540  
     0.77%   5066       1      enc.c:1335   enc.c:1325  
     0.76%   5014       6      dec.c:299    dec.c:299   
     0.72%   4770       6      dec.c:174    dec.c:174   
     0.71%   4681       2      dec.c:396    dec.c:395   
     0.69%   4563       3      dec.c:174    dec.c:174   
     0.58%   3804      24      dec.c:174    dec.c:174   
```

请注意，我们添加了 `-F +cycles` 选项以在输出中显示周期计数（“BBCycles” 列）。为适应页面大小，我们删除了几行无关紧要的 `perf report` 输出。让我们关注源代码和目标代码都是 `dec.c:174` 的行，输出中有七行这样的行。在源代码中，行 `dec.c:174` 展开了一个包含自包含分支的宏。这就是为什么源代码和目标代码恰好位于同一行的原因。

Linux `perf` 首先按开销对条目进行排序，因此我们需要手动过滤我们感兴趣的分支的条目。幸运的是，它们可以通过 `grep` 命令轻松过滤。事实上，如果我们过滤它们，我们将得到以这个分支结尾的基本块的延迟分布，如表 {@tbl:bb_latency} 所示。这些数据可以绘制成一个类似于图 @fig:LBR_timing_BB 的图表。

周期 | 样本数 | 概率密度
------ | -------- | --------
1 | 10484 | 17.0%
2 | 16728 | 27.1%
3 | 4563 | 7.4%
4 | 15815 | 25.6%
6 | 4770 | 7.7%
24 | 3804 | 6.2%
32 | 5567 | 9.0%

表: 基本块延迟的概率密度。 {#tbl:bb_latency}

以下是我们如何解释这些数据：从所有收集的样本中，17% 的时间基本块的延迟为 1 个周期，27% 的时间为 2 个周期，等等。请注意，分布主要集中在 1 到 6 个周期，但也有第二个模式，延迟高得多，为 24 和 32 个周期，这可能对应于分支预测错误惩罚。分布中的第二个模式占所有样本的 15%。

这个例子表明，不仅可以绘制微型基准测试的基本块延迟，还可以绘制实际应用程序的基本块延迟。目前，LBR 是英特尔系统上最精确的周期级计时信息源。

### 估计分支结果概率

在后面的 [@sec:secFEOpt] 部分，我们将讨论代码布局对性能的重要性。 进一步说，以透底方式放置热路径[^11] 通常可以提高程序性能。 知道某个分支最常见的执行结果可以让开发人员和编译器做出更好的优化决策。例如，如果一个分支有 99% 的时间被执行，我们可以尝试反转条件将其转换为未执行分支。

LBR 可以让我们在不检测代码的情况下收集这些数据。 分析结果将为用户提供条件真假结果之间的比率，即分支被执行和未执行的次数。 这一特性在分析间接跳转（switch 语句）和间接调用（虚函数调用）时尤其有用。 您可以在 easyperf 博客上找到实际应用示例：[https://easyperf.net/blog/2019/05/06/Estimating-branch-probability](https://easyperf.net/blog/2019/05/06/Estimating-branch-probability)[^6]。

### 提供编译器反馈数据

我们将在后面的 [@sec:secPGO] 部分讨论基于配置文件的优化 (PGO)，这里先简要提一下。 分支记录机制可以为优化编译器提供配置文件反馈数据。 想象一下，我们可以将我们在前面部分发现的所有数据反馈给编译器。 在某些情况下，这些数据无法使用传统的静态代码检测工具获得，因此分支记录机制不仅因开销更低而成为更好的选择，而且还能提供更丰富的配置文件数据。 依赖硬件 PMU 收集数据进行的 PGO 工作流程越来越流行，一旦 AMD 和 ARM 的支持成熟，可能会迅速发展。

[^2]: Linux `perf script` 手册页 - [http://man7.org/linux/man-pages/man1/perf-script.1.html](http://man7.org/linux/man-pages/man1/perf-script.1.html).
[^5]: perf 生成的报告头可能仍然让人困惑，因为它说 "21K of event cycles"。 但这里有 "21K" 个 LBR 条目，而不是 "cycles"。
[^6]: Easyperf: 估计分支概率 - [https://easyperf.net/blog/2019/05/06/Estimating-branch-probability](https://easyperf.net/blog/2019/05/06/Estimating-branch-probability)
[^7]: LLVM 测试套件 7zip 基准 - [https://github.com/llvm-mirror/test-suite/tree/master/MultiSource/Benchmarks/7zip](https://github.com/llvm-mirror/test-suite/tree/master/MultiSource/Benchmarks/7zip)
[^9]: Easyperf: 为任意基本块的延迟构建概率密度图 - [https://easyperf.net/blog/2019/04/03/Precise-timing-of-machine-code-with-Linux-perf](https://easyperf.net/blog/2019/04/03/Precise-timing-of-machine-code-with-Linux-perf).
[^11]: 也就是说，当热分支没有被执行时。

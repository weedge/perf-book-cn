### 在英特尔平台上的 TMA {#sec:secTMA_Intel}

TMA方法学首次由英特尔于2014年提出，并从SandyBridge系列处理器开始提供支持。英特尔的实现支持每个高级别桶的嵌套类别，从而更好地了解程序中的CPU性能瓶颈（参见图@fig:TMA）。

该工作流程旨在“深入挖掘(drill down)”TMA层次结构的较低级别，直到我们达到对性能瓶颈的非常具体的分类为止。例如，首先，我们收集主要的四个桶的指标：`Front End Bound`、`Back End Bound`、`Retiring`、`Bad Speculation`。比如，我们发现程序执行的大部分时间被内存访问阻塞了（这是`Back End Bound`桶，参见图@fig:TMA）。接下来的步骤是再次运行工作负载，并仅收集与`Memory Bound`桶有关的特定指标。这个过程重复进行，直到我们知道确切的根本原因，例如，`L3 Bound`。

![TMA性能瓶颈的层次结构。*© Image by Ahmad Yasin.*](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/pmu-features/TMAM.png)<div id="TMA"></div>

多次运行工作负载并在每次运行时专注于特定指标是完全可以的。但通常，运行一次工作负载并收集所有TMA各级别所需的所有指标就足够了。性能分析工具通过在单次运行中在不同性能事件之间进行多路复用（参见[@sec:secMultiplex]）来实现这一点。此外，在现实应用中，性能可能受到多个因素的限制。例如，它可以同时经历大量的分支错误预测（`Bad Speculation`）和缓存丢失（`Back End Bound`）。在这种情况下，TMA将同时深入挖掘多个桶，并确定每种类型的瓶颈对程序性能的影响。像英特尔的VTune Profiler、AMD的uProf和Linux的`perf`等分析工具可以在单次基准测试运行中计算所有TMA指标。但是，这仅在工作负载稳定时才可行。否则，最好回到多次运行和每次运行都进行深入挖掘的原始策略。

TMA的前两个级别的指标以所有流水线插槽的百分比表示（参见[@sec:PipelineSlot]），这些插槽在程序执行期间是可用的。这使得TMA能够准确表示CPU微体系结构的利用率，考虑到处理器的全部带宽。到目前为止，所有内容都应该很好地总结为100%。然而，从第3级开始，桶可能以不同的计数域表示，例如时钟和停顿。因此，它们不一定与其他TMA桶直接可比。

TMA的第一步是识别程序中的性能瓶颈。在完成这一步之后，我们需要知道问题具体出现在代码的哪里。TMA的第二步是将问题的源头定位到代码的确切行和汇编指令。该分析方法提供了应针对性能问题的每个类别使用的确切性能事件。然后，您可以在此事件上进行采样，以找到在第一阶段识别的性能瓶颈所在的源代码行。如果这个过程让您感到困惑，不用担心，阅读案例研究后一切都会变得清晰。

## 案例研究：使用 TMA 减少缓存未命中数量 

作为本案例研究的示例，我们采用了非常简单的基准测试，使其易于理解和更改。它显然不能代表现实世界的应用程序，但足以演示 TMA 的工作流程。本书的第二部分中有更多实用的例子。

本书的大部分读者可能会将 TMA 应用于他们熟悉自己的应用程序。但即使您是第一次看到该应用程序，TMA 也非常有效。因此，我们不会首先向您展示基准测试的原始源代码。但这里有一个简短的描述：基准测试在堆上分配了一个 200 MB 的数组，然后进入一个 100M 次迭代的循环。在循环的每次迭代中，它都会生成一个指向已分配数组的随机索引，执行一些虚拟工作，然后从该索引读取值。

我们使用配备有 Intel Core i5-8259U CPU（基于 Skylake）和 16GB DRAM（DDR4 2400 MT/s）的机器运行实验，运行 64 位 Ubuntu 20.04（内核版本 5.13.0-27）。

### 步骤 1：识别瓶颈 

作为第一步，我们运行微基准测试并收集一组有限的事件，这些事件将帮助我们计算第 1 级指标。在这里，我们尝试通过将它们归因于四个 L1 桶（“前端受限”、“后端受限”、“退休”、“错误猜测”）来识别应用程序的高级性能瓶颈。可以使用 Linux `perf` 工具收集第 1 级指标。从 Linux 内核 4.8 开始，`perf` 在 `perf stat` 命令中有一个 `--topdown` 选项，用于打印 TMA 第 1 级指标。以下是我们基准测试的细分。本部分的命令输出经过修剪以节省空间。


 ```bash
$ perf stat --topdown -a -- taskset -c 0 ./benchmark.exe
       retiring  bad speculat  FE bound  BE bound
S0-C0    32.5%       0.2%       13.8%      53.4%  <==
S0-C1    17.4%       2.3%       12.0%      68.2%
S0-C2    10.1%       5.8%       32.5%      51.6%
S0-C3    47.3%       0.3%        2.9%      49.6%
...
```

为了获得高级 TMA 指标的值，Linux `perf` 需要分析整个系统 (`-a`)。这就是为什么我们看到所有内核的指标。但是由于我们已经使用 `taskset -c 0` 将基准测试固定在核心 0 上，因此我们只需要关注与 `S0-C0` 对应的行。我们可以丢弃其他行，因为它们正在运行其他任务或处于空闲状态。通过查看输出，我们可以判断应用程序的性能受 CPU 后端限制。现在先不进行分析，让我们向下钻取一层。

Linux perf 只支持 1 级 TMA 指标，因此要访问 2、3 级及更高级别的 TMA 指标，我们将使用 `toplev` 工具，它是 Andi Kleen 编写的 pmu-tools: [https://github.com/andikleen/pmu-tools](https://github.com/andikleen/pmu-tools)[^7] 的一部分。它用 Python 实现，并在幕后调用 Linux `perf`。要使用 `toplev`，必须启用特定的 Linux 内核设置，有关详细信息，请查看文档。

```bash
$ ~/pmu-tools/toplev.py --core S0-C0 -l2 -v --no-desc taskset -c 0 ./benchmark.exe
...
# Level 1
S0-C0  Frontend_Bound:                13.92 % Slots 
S0-C0  Bad_Speculation:                0.23 % Slots 
S0-C0  Backend_Bound:                 53.39 % Slots      
S0-C0  Retiring:                      32.49 % Slots   
# Level 2
S0-C0  Frontend_Bound.FE_Latency:     12.11 % Slots 
S0-C0  Frontend_Bound.FE_Bandwidth:    1.84 % Slots 
S0-C0  Bad_Speculation.Branch_Mispred: 0.22 % Slots 
S0-C0  Bad_Speculation.Machine_Clears: 0.01 % Slots 
S0-C0  Backend_Bound.Memory_Bound:    44.59 % Slots <==
S0-C0  Backend_Bound.Core_Bound:       8.80 % Slots 
S0-C0  Retiring.Base:                 24.83 % Slots 
S0-C0  Retiring.Microcode_Sequencer:   7.65 % Slots    
```

在此命令中，我们还将进程固定到 CPU0（使用 `taskset -c 0`），并将 `toplev` 的输出仅限于此核心（`--core S0-C0`）。选项 `-l2` 告诉工具收集 Level 2 指标。选项 `--no-desc` 禁用每个指标的描述。

我们可以看到，应用程序的性能受内存访问限制（`Backend_Bound.Memory_Bound`）。近一半的 CPU 执行资源都浪费在等待内存请求完成上。现在让我们更深入地挖掘一次：[^17]

```bash
$ ~/pmu-tools/toplev.py --core S0-C0 -l3 -v --no-desc taskset -c 0 ./benchmark.exe
...
# Level 1
S0-C0    Frontend_Bound:                 13.91 % Slots
S0-C0    Bad_Speculation:                 0.24 % Slots
S0-C0    Backend_Bound:                  53.36 % Slots
S0-C0    Retiring:                       32.41 % Slots
# Level 2
S0-C0    FE_Bound.FE_Latency:            12.10 % Slots
S0-C0    FE_Bound.FE_Bandwidth:           1.85 % Slots
S0-C0    BE_Bound.Memory_Bound:          44.58 % Slots
S0-C0    BE_Bound.Core_Bound:             8.78 % Slots
# Level 3
S0-C0-T0 BE_Bound.Mem_Bound.L1_Bound:     4.39 % Stalls
S0-C0-T0 BE_Bound.Mem_Bound.L2_Bound:     2.42 % Stalls
S0-C0-T0 BE_Bound.Mem_Bound.L3_Bound:     5.75 % Stalls
S0-C0-T0 BE_Bound.Mem_Bound.DRAM_Bound:  47.11 % Stalls <==
S0-C0-T0 BE_Bound.Mem_Bound.Store_Bound:  0.69 % Stalls
S0-C0-T0 BE_Bound.Core_Bound.Divider:     8.56 % Clocks
S0-C0-T0 BE_Bound.Core_Bound.Ports_Util: 11.31 % Clocks
```

我们发现瓶颈在于 `DRAM_Bound`。这告诉我们，许多内存访问都会错过所有级别的缓存，并一直到达主内存。如果我们收集程序的 L3 缓存未命中绝对数量，也可以确认这一点。对于 Skylake 架构，`DRAM_Bound` 指标是使用 `CYCLE_ACTIVITY.STALLS_L3_MISS` 性能事件计算的。让我们手动收集它：

```bash
$ perf stat -e cycles,cycle_activity.stalls_l3_miss -- ./benchmark.exe
  32226253316  cycles
  19764641315  cycle_activity.stalls_l3_miss
```

`CYCLE_ACTIVITY.STALLS_L3_MISS` 事件会计算执行停顿时的周期数，而 L3 缓存未命中需求加载尚未完成。我们可以看到大约有 60% 的此类周期，这非常糟糕。

### 步骤 2：定位代码中的位置 

TMA 过程的第二个步骤是找到性能事件最频繁发生的代码位置。为此，应该使用与步骤 1 中确定的瓶颈类型相对应的事件对工作负载进行采样。

查找此类事件的推荐方法是使用 `toplev` 工具的 `--show-sample` 选项，该选项将建议可用于定位问题的 `perf record` 命令行。为了理解 TMA 的机制，我们还介绍了手动查找与特定性能瓶颈关联的事件的方法。性能瓶颈和用于确定瓶颈在源代码中的位置的性能事件之间的对应关系可以使用 TMA metrics: [https://github.com/intel/perfmon/blob/main/TMA_Metrics.xlsx](https://github.com/intel/perfmon/blob/main/TMA_Metrics.xlsx)[^2] 表格来完成。`Locate-with` 列表示用于定位问题发生确切代码位置的性能事件。在我们的例子中，为了找到导致 `DRAM_Bound` 指标如此高的内存访问（L3 缓存未命中），我们应该对 `MEM_LOAD_RETIRED.L3_MISS_PS` 精确事件进行采样。以下是示例命令：

```bash
$ perf record -e cpu/event=0xd1,umask=0x20,name=MEM_LOAD_RETIRED.L3_MISS/ppp ./benchmark.exe

$ perf report -n --stdio
...
# Samples: 33K of event ‘MEM_LOAD_RETIRED.L3_MISS’
# Event count (approx.): 71363893
# Overhead   Samples  Shared Object   Symbol
# ........  ......... ..............  .................
#
    99.95%    33811   benchmark.exe   [.] foo                
     0.03%       52   [kernel]        [k] get_page_from_freelist
     0.01%        3   [kernel]        [k] free_pages_prepare
     0.00%        1   [kernel]        [k] free_pcppages_bulk
```

几乎所有 L3 未命中都是由可执行文件 `benchmark.exe` 中的函数 `foo` 中的内存访问引起的。现在是时候查看基准测试的源代码了，可以在 Github: [https://github.com/dendibakh/dendibakh.github.io/tree/master/_posts/code/TMAM](https://github.com/dendibakh/dendibakh.github.io/tree/master/_posts/code/TMAM) 上找到。[^8]

为了避免编译器优化，函数 `foo` 是用汇编语言实现的，如 [@lst:TMA_asm] 所示。基准测试的“驱动”部分在 `main` 函数中实现，如 [@lst:TMA_cpp] 所示。我们分配了一个足够大的数组 `a` 以使其不适合 6MB 的 L3 缓存。基准测试生成一个指向数组 `a` 的随机索引，并将此索引与数组 `a` 的地址一起传递给 `foo` 函数。稍后，`foo` 函数会读取此随机内存位置。[^11]

代码清单：函数 foo 的汇编代码。 {#lst:TMA_asm}
```bash
$ perf annotate --stdio -M intel foo
Percent |  Disassembly of benchmark.exe for MEM_LOAD_RETIRED.L3_MISS
------------------------------------------------------------
        :  Disassembly of section .text:
        :
        :  0000000000400a00 <foo>:
        :  foo():
   0.00 :    400a00:  nop  DWORD PTR [rax+rax*1+0x0]
   0.00 :    400a08:  nop  DWORD PTR [rax+rax*1+0x0]
                 ...
 100.00 :    400e07:  mov  rax,QWORD PTR [rdi+rsi*1] <==
                 ...
   0.00 :    400e13:  xor  rax,rax
   0.00 :    400e16:  ret 
```

Listing: Source code of function main. {#lst:TMA_cpp}

```cpp
extern "C" { void foo(char* a, int n); }
const int _200MB = 1024*1024*200;
int main() {
  char* a = (char*)malloc(_200MB); // 200 MB buffer
  ...
  for (int i = 0; i < 100000000; i++) {
    int random_int = distribution(generator);
    foo(a, random_int);
  }
  ...
}
```

通过查看 [@lst:TMA_asm]，我们可以看到函数 `foo` 中的所有 L3 缓存未命中都被标记为单个指令。现在我们知道是哪条指令导致了这么多 L3 未命中，让我们来修复它。

### 步骤 3：修复问题 

请记住，在 `foo` 函数的开头有用 NOP 模拟的虚拟工作。这会在我们获得将要访问的下一个地址的那一刻与实际加载指令之间创建一个时间窗口。这个时间窗口的存在使我们有机会在虚拟工作的同时开始预取内存位置。[@lst:TMA_prefetch] 展示了这个想法。有关显式内存预取技术的更多信息，请参阅 [@sec:memPrefetch]。

列表：在 main 中插入内存预取。 {#lst:TMA_prefetch}

```cpp
  for (int i = 0; i < 100000000; i++) {
    int random_int = distribution(generator);
+   __builtin_prefetch ( a + random_int, 0, 1);
    foo(a, random_int);
  }
```

通过这个显式的内存预取提示，执行时间从 8.5 秒减少到 6.5 秒。此外，`CYCLE_ACTIVITY.STALLS_L3_MISS` 事件的数量几乎减少了十倍：从 19B 减少到 2B。

TMA 是一个迭代过程，因此一旦我们修复了一个问题，我们就需要从步骤 1 开始重复该过程。它可能会将瓶颈移动到另一个桶中，在本例中是“退休”。这是一个演示 TMA 方法工作流程的简单示例。分析现实世界的应用程序不太可能那么容易。本书第二部分的章节组织得井井有条，以便与 TMA 流程一起使用。特别是，第 8 章涵盖“内存受限”类别，第 9 章涵盖“核心受限”，第 10 章涵盖“错误猜测”，第 11 章涵盖“前端受限”。这种结构的目的是形成一个清单，供您在遇到特定性能瓶颈时用于驱动代码更改。

#### 其他资源和链接 

- Ahmad Yasin 的论文“用于性能分析和计数器架构的顶向下方法” [[@TMA_ISPASS](../References.md#TMA_ISPASS)]。
- Ahmad Yasin 在 IDF'15 上的演讲“使用英特尔 Skylake 的顶向下分析使软件优化变得简单”，网址： [https://youtu.be/kjufVhyuV_A](https://youtu.be/kjufVhyuV_A)。
- Andi Kleen 的博客：pmu-tools，第二部分：toplev，网址： [http://halobates.de/blog/p/262](http://halobates.de/blog/p/262)。
- Toplev 手册，网址： [https://github.com/andikleen/pmu-tools/wiki/toplev-manual](https://github.com/andikleen/pmu-tools/wiki/toplev-manual)。

[^2]: TMA 指标 - [https://github.com/intel/perfmon/blob/main/TMA_Metrics.xlsx](https://github.com/intel/perfmon/blob/main/TMA_Metrics.xlsx).
[^7]: PMU 工具 - [https://github.com/andikleen/pmu-tools](https://github.com/andikleen/pmu-tools).
[^8]: 案例研究示例 - [https://github.com/dendibakh/dendibakh.github.io/tree/master/_posts/code/TMAM](https://github.com/dendibakh/dendibakh.github.io/tree/master/_posts/code/TMAM).
[^11]: 根据 x86 调用约定 ([https://en.wikipedia.org/wiki/X86_calling_conventions](https://en.wikipedia.org/wiki/X86_calling_conventions)), 前两个参数分别位于 `rdi` 和 `rsi` 寄存器中。
[^17]: 由于我们知道应用程序受内存限制，因此我们可以改用 `-l2 --nodes L1_Bound,L2_Bound,L3_Bound,DRAM_Bound,Store_Bound` 选项而不是 `-l3` 来限制收集。

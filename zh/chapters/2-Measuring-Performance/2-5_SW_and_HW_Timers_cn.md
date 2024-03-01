## 软件和硬件定时器 {#sec:timers}

为了对执行时间进行基准测试，工程师通常会使用现代平台提供的两种不同的定时器：

- **系统范围的高分辨率定时器**：这是一个系统定时器，通常实现为自从一个任意的起始日期（称为[纪元](https://en.wikipedia.org/wiki/Epoch_(computing))）[^1]以来经过的时钟周期数。这个时钟是单调的；即它总是递增的。可以通过系统调用从操作系统中获取系统时间。[^2]在Linux系统上，可以通过`clock_gettime`系统调用来访问系统定时器。系统定时器具有纳秒级分辨率，在所有CPU之间保持一致，并且与CPU频率无关。虽然系统定时器可以返回纳秒精度的时间戳，但由于通过`clock_gettime`系统调用获取时间戳需要很长时间，因此不适合测量短时间内发生的事件。但是对于持续时间超过一微秒的事件来说，这是可以接受的。在C++中访问系统定时器的`de facto`标准是使用`std::chrono`，如[@lst:Chrono](#Chrono)所示。

  代码清单：使用C++ std::chrono访问系统定时器 
<div id="Chrono"></div>

  ```cpp
  #include <cstdint>
  #include <chrono>

  // 返回经过的纳秒数
  uint64_t timeWithChrono() {
    using namespace std::chrono;
    auto start = steady_clock::now();
    // 运行一些代码
    auto end = steady_clock::now();
    uint64_t delta = duration_cast<nanoseconds>
        (end - start).count();
    return delta;
  }
  ```

- **时间戳计数器（TSC）**：这是一种硬件定时器，实现为硬件寄存器。TSC是单调的，并且具有恒定的速率，即不考虑频率变化。每个CPU都有自己的TSC，它只是已经过去的参考周期数（参见[@sec:secRefCycles]）。适用于持续时间从纳秒到一分钟的短事件的测量。可以使用编译器内置函数`__rdtsc`来获取TSC的值，如[@lst:TSC](#TSC)所示，该函数在底层使用`RDTSC`汇编指令。有关使用`RDTSC`汇编指令对代码进行基准测试的更低级别的详细信息，可以参考白皮书[[@IntelRDTSC](../References.md#IntelRDTSC)]。

  代码清单：使用__rdtsc编译器内置函数访问TSC <div id="TSC"></div>

  ```cpp
  #include <x86intrin.h>
  #include <cstdint>
  
  // 返回经过的参考时钟数
  uint64_t timeWithTSC() {
      uint64_t start = __rdtsc();
      // 运行一些代码
      return __rdtsc() - start;
  }
  ```

选择使用哪种定时器非常简单，取决于您要测量的事物持续的时间有多长。如果您要测量的时间很短，TSC会给出更高的精度。相反，使用TSC来测量运行数小时的程序是没有意义的。除非您确实需要周期精度，否则系统定时器应该足够用于大多数情况。要记住的重要一点是，访问系统定时器通常的延迟比访问TSC要高。进行`clock_gettime`系统调用可能比执行`RDTSC`指令慢十倍以上，后者需要20多个CPU周期。这在尤其需要最小化测量开销时可能变得很重要，尤其是在生产环境中。有关在各种平台上访问定时器的不同API的性能比较可在CppPerformanceBenchmarks存储库的[wiki页面](https://gitlab.com/chriscox/CppPerformanceBenchmarks/-/wikis/ClockTimeAnalysis)[^3]上找到。

[^1]: Unix纪元从1970年1月1日00:00:00 UT开始：[https://en.wikipedia.org/wiki/Unix_epoch](https://en.wikipedia.org/wiki/Unix_epoch)。
[^2]: 检索系统时间 - [https://en.wikipedia.org/wiki/System_time#Retrieving_system_time](https://en.wikipedia.org/wiki/System_time#Retrieving_system_time)
[^3]: CppPerformanceBenchmarks wiki - [https://gitlab.com/chriscox/CppPerformanceBenchmarks/-/wikis/ClockTimeAnalysis](https://gitlab.com/chriscox/CppPerformanceBenchmarks/-/wikis/ClockTimeAnalysis)

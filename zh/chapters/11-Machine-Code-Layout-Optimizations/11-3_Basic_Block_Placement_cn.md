## 基本块布局

假设我们在程序中有一个热路径，其中有一些错误处理代码（`coldFunc`）：

```c++
// 热路径
if (cond)
  coldFunc();
// 再次热路径
```

图 @fig:BBLayout 显示了这段代码的两种可能的物理布局。如果没有提供任何提示，图 @fig:BB_default 是大多数编译器默认会生成的布局。如果我们反转条件 `cond` 并将热代码放置为 fall through，则可以实现图 @fig:BB_better 中所示的布局。

<div id="fig:BBLayout">

![默认布局](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/cpu_fe_opts/BBLayout_Default.png){#fig:BB_default width=40%}
![改进的布局](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/cpu_fe_opts/BBLayout_Better.png){#fig:BB_better width=40%}

上面代码片段的两种机器代码布局版本。
</div>

哪种布局更好？这取决于 `cond` 通常是真还是假。如果 `cond` 通常为真，那么我们最好选择默认布局，因为否则我们会执行两次跳转而不是一次。另外，在一般情况下，如果 `coldFunc` 是一个相对较小的函数，我们希望它被内联。但是，在这个特定的例子中，我们知道 coldFunc 是一个错误处理函数，可能不会经常执行。通过选择布局 @fig:BB_better，我们在代码的热部分之间保持 fall through，并将 taken branch 转换为 not taken branch。

图 @fig:BB_better 中呈现的布局性能更好，原因有几个。首先，图 @fig:BB_better 中的布局更好地利用了指令和 $\mu$op-cache（DSB，参见 [@sec:uarchFE]）。所有热代码都连续，没有缓存行碎片：L1I-cache 中的所有缓存行都被热代码使用。$\mu$op-cache 也是如此，因为它也是基于底层代码布局进行缓存的。其次，taken branch 对于 fetch 单元来说也更昂贵。CPU 前端会连续获取字节块，因此每次 taken jump 都意味着 jump 之后的字节是无用的。这会降低最大有效提取吞吐量。最后，在某些架构上，not taken branch 比 taken branch 便宜。例如，Intel Skylake CPU 每周期可以执行两个 untaken branch，但每两周期只能执行一个 taken branch。[^2]

为了建议编译器生成改进版本的机器代码布局，可以使用 `[[likely]]`[^10] 和 `[[unlikely]]` 属性提供提示，该属性从 C++20 开始可用。使用此提示的代码如下所示：

```c++
// 热路径
if (cond) [[unlikely]]
  coldFunc();
// 再次热路径
```

在上面代码中，`[[unlikely]]` 提示将指示编译器 `cond` 不太可能为真，因此编译器应相应地调整代码布局。在 C++20 之前，开发人员可以使用 `__builtin_expect`: [https://llvm.org/docs/BranchWeightMetadata.html#builtin-expect](https://llvm.org/docs/BranchWeightMetadata.html#builtin-expect)[^3] 构造，他们通常自己创建 `LIKELY` wrapper 提示以使代码更具可读性。例如：

```c++
#define LIKELY(EXPR) __builtin_expect((bool)(EXPR), true)
#define UNLIKELY(EXPR) __builtin_expect((bool)(EXPR), false)
// 热路径
if (UNLIKELY(cond)) // NOT
  coldFunc();
// 再次热路径
```

优化编译器不仅会在遇到“likely/unlikely”提示时改进代码布局。他们还会在其他地方利用这些信息。例如，当应用 `[[unlikely]]` 属性时，编译器将阻止内联 `coldFunc`，因为它现在知道它不太可能经常被执行，并且优化它的大小更有利，即只留下一个 `CALL` 到这个函数。插入 `[[likely]]` 属性对于 switch 语句也是可能的，如 [@lst:BuiltinSwitch] 所示。


代码清单:switch语句中可能使用的属性 {#lst:BuiltinSwitch .cpp}
```cpp
for (;;) {
  switch (instruction) {
               case NOP: handleNOP(); break;
    [[likely]] case ADD: handleADD(); break;
               case RET: handleRET(); break;
    // handle other instructions
  }
}
```

使用此提示，编译器将能够稍微重新排序代码并优化热交换以更快地处理 `ADD` 指令。

[^2]: 不过，有一个特殊的微型循环优化，可以使非常小的循环每个周期执行一个 taken branch。
[^3]: 有关 builtin-expect 的更多信息，请参见此处：[https://llvm.org/docs/BranchWeightMetadata.html#builtin-expect](https://llvm.org/docs/BranchWeightMetadata.html#builtin-expect)。
[^10]: C++ 标准 `[[likely]]` 属性：[https://en.cppreference.com/w/cpp/language/attributes/likely](https://en.cppreference.com/w/cpp/language/attributes/likely)。

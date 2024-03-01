## 函数拆分

函数拆分的思想是将热点代码与冷代码分开。这种转换通常也被称为*函数轮廓化*。这种优化对于具有复杂控制流图和热路径中存在大量冷代码块的相对较大函数非常有益。[@lst:FunctionSplitting1](#FunctionSplitting1) 中显示了这种转换可能会有益处的代码示例。为了将热路径中的冷基本块移除，我们将它们剪切并粘贴到一个新函数中，并创建一个调用它们的调用。

代码清单：函数拆分：将冷代码轮廓化到新函数。 <div id="FunctionSplitting1"></div>

```cpp
void foo(bool cond1, bool cond2) {              void foo(bool cond1, bool cond2) {
  // 热路径                                        // 热路径
  if (cond1) {                                    if (cond1) {
    /* 大量的冷代码 (1) */                            cold1(); 
  }                                               }
  // 热路径                                        // 热路径
  if (cond2) {                            =>      if (cond2) {
    /* 大量的冷代码 (2) */                            cold2(); 
  }                                               }
}                                               }
                                                void cold1() __attribute__((noinline)) 
                                                  { /* 大量的冷代码 (1) */ }
                                                void cold2() __attribute__((noinline))
                                                  { /* 大量的冷代码 (2) */ }
```

请注意，我们通过使用 `noinline` 属性禁用了冷函数的内联。因为如果没有这个属性，编译器可能会决定内联它，这实际上会撤销我们的转换。或者，我们可以在 `cond1` 和 `cond2` 分支上都应用 `[[unlikely]]` 宏（参见[@sec:secLIKELY]），以传达给编译器不希望内联 `cold1` 和 `cold2` 函数。

图[@fig:FunctionSplitting](#FunctionSplitting) 给出了这种转换的图形表示。因为我们在热路径中只留下了一个 `CALL` 指令，所以下一个热指令很可能会与上一个指令驻留在同一个缓存行中。这提高了 CPU 前端数据结构（如 I-cache 和 DSB）的利用率。

<div id="FunctionSplitting">

![默认布局](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/cpu_fe_opts/FunctionSplitting_Default.png)<div id="FuncSplit_default"></div>
![改进的布局](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/cpu_fe_opts/FunctionSplitting_Improved.png)<div id="FuncSplit_better"></div>

将冷代码拆分到单独的函数中。
</div>

轮廓化的函数应该创建在 `.text` 段之外，例如在 `.text.cold` 中。如果函数从不被调用，这样做可以提高内存占用，因为它在运行时不会加载到内存中。
## 用谓词替换分支 {#sec:BranchlessPredication}

某些分支可以通过执行分支的两部分，然后选择正确的结果（*谓词*）来有效地消除。当这种转换可能有利可图时，代码示例显示在 [@lst:PredicatingBranchesCode](#PredicatingBranchesCode) 中。如果 TMA 提示 `if (cond)` 分支具有非常高的误判率，您可以尝试通过执行右侧显示的转换来消除分支。

代码清单：谓词分支。 <div id="PredicatingBranchesCode"></div>

```cpp
int a;                                             int x = computeX();
if (cond) { /* frequently mispredicted */   =>     int y = computeY();
  a = computeX();                                  int a = cond ? x : y;
} else {
  a = computeY();
}
```

对于右侧的代码，编译器可以替换来自三元运算符的分支，并生成 `CMOV` x86 指令。`CMOVcc` 指令检查 `EFLAGS` 寄存器（`CF、OF、PF、SF` 和 `ZF`）中一个或多个状态标志的状态，并在标志处于特定状态或条件下执行移动操作。可以使用 `FCMOVcc,VMAXSS/VMINSS` 指令对浮点数字进行类似的转换。[@lst:PredicatingBranchesAsm](#PredicatingBranchesAsm) 显示了原始版本和无分支版本的汇编列表。

代码清单：谓词分支 - x86 汇编代码。 <div id="PredicatingBranchesAsm"></div>

```asm
# original version                  # branchless version
400504: test edi,edi                400537: mov eax,0x0
400506: je 400514                   40053c: call <computeX> # compute x; a = x
400508: mov eax,0x0                 400541: mov ebp,eax     # ebp = x
40050d: call <computeX>      =>     400543: mov eax,0x0
400512: jmp 40051e                  400548: call <computeY> # compute y; a = y
400514: mov eax,0x0                 40054d: test ebx,ebx    # test cond
400519: call <computeY>             40054f: cmovne eax,ebp  # override a with x if needed
40051e: mov edi,eax
```

与原始版本相比，无分支版本没有跳转指令。然而，无分支版本独立计算 `x` 和 `y`，然后选择其中一个值并丢弃另一个值。虽然这种转换消除了分支预测错误的惩罚，但它可能比原始代码做了更多的工作。在这种情况下，性能改进在很大程度上取决于 `computeX` 和 `computeY` 函数的特性。如果函数很小，编译器能够内联它们，那么它可能会带来明显的性能提升。如果函数很大，执行这两个函数的成本可能比承担分支预测错误的成本更低。

需要注意的是，谓词并不总是能提高应用程序的性能。谓词的问题在于它限制了 CPU 的并行执行能力。对于原始版本的代码，CPU 可以预测分支将被取走，推测性地调用 `computeX` 并继续执行程序的其余部分。对于无分支版本，这种类型的推测是不可能的，因为 CPU 必须等待 `CMOVNE` 指令的结果才能继续进行。

在选择代码的常规版本和无分支版本之间进行权衡时，典型的例子是二分查找[^3]：

* **对于无法放入 CPU 缓存的大型数组的搜索，基于分支的二分查找版本性能更好**，因为分支预测错误的惩罚与内存访问的延迟相比很低（由于缓存未命中，延迟很高）。由于存在分支，CPU 可以推测其结果，从而允许同时从当前迭代和下一个迭代加载数组元素。它并没有就此结束：推测仍在继续，您可能同时有多个加载正在进行。
* **对于适合 CPU 缓存的小型数组，情况则相反**。正如前面所解释的，无分支搜索仍然将所有内存访问序列化。但这一次，加载延迟很小（只有少数周期），因为数组适合 CPU 缓存。基于分支的二分查找会不断遭受误判，其成本大约为 10-20 个周期。在这种情况下，误判的成本远高于内存访问的成本，因此推测执行的优势会受到阻碍。无分支版本通常在这种情况下更快。

二分查找是一个很好的例子，它展示了如何在选择标准实现和无分支实现时进行推理。现实世界的场景可能更难分析，因此，再次测量以找出在您的情况下替换分支是否有益。

如果没有性能分析数据，编译器就无法了解误判率。因此，编译器通常默认生成分支（即原始版本）。它们在使用谓词方面比较保守，即使在简单的情况下也可能抵制生成 `CMOV` 指令。同样，权衡也很复杂，如果没有运行时数据，就很难做出正确的决定。基于硬件的 PGO（参见 [#sec:secPGO]）将是这里的一大进步。此外，还有一种方法可以通过硬件机制向编译器指示分支条件是不可预测的。从 Clang-17 开始，编译器现在支持 `__builtin_unpredictable`，它可以非常有效地将不可预测的分支替换为 `CMOV` x86 指令。例如：

```cpp
if (__builtin_unpredictable(x != 2))
  y = 0;
if (__builtin_unpredictable(x == 3))
  y = 1;
```


[^3]: 关于无分支二分查找的讨论 - [https://stackoverflow.com/a/54273248](https://stackoverflow.com/a/54273248)。

## 用算术替换分支

在某些情况下，可以用算术来替换分支。如[@lst:LookupBranches]中的代码，也可以使用简单的算术公式重写，如[@lst:ArithmeticBranches]所示。对于这段代码，Clang-17 编译器用更便宜的乘法运算替换了昂贵的除法运算。

**代码清单：** 用算术替换分支。

```cpp
int8_t mapToBucket(unsigned v) {
  constexpr unsigned BucketRangeMax = 50;
  if (v < BucketRangeMax)
    return v / 10;
  return -1;
}
```

截至2023年，编译器通常无法自行找到这些捷径，因此由程序员手动完成。如果你能找到用算术替换分支的方法，你很可能会看到性能改进。不幸的是，这并不总是可能的。
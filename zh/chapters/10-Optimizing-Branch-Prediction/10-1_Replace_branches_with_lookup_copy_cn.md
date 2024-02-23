## 用查找表替换分支

避免频繁出现分支预测错误的一种方法是使用查找表。在[@lst:LookupBranches]中展示了一个可能会受益于这种转换的代码示例。与往常一样，原始版本在左侧，改进版本在右侧。函数 `mapToBucket` 将 `[0-50)` 范围内的值映射到对应的五个桶中，并对超出此范围的值返回 `-1`。对于均匀分布的 `v` 值，`v` 有相等的概率落入任何一个桶中。在原始版本的生成的汇编中，我们可能会看到许多分支，这可能会导致高的分支预测错误率。希望可以通过单个数组查找来重写函数 `mapToBucket`，如右侧所示。

**代码清单：** 用查找表替换分支。

```cpp
int8_t mapToBucket(unsigned v) {              int8_t buckets[50] = {
  if (v >= 0  && v < 10) return 0;              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  if (v >= 10 && v < 20) return 1;              1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
  if (v >= 20 && v < 30) return 2;     =>       2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
  if (v >= 30 && v < 40) return 3;              3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
  if (v >= 40 && v < 50) return 4;              4, 4, 4, 4, 4, 4, 4, 4, 4, 4};
  return -1;
}                                             int8_t mapToBucket(unsigned v) {
                                                if (v < (sizeof(buckets) / sizeof(int8_t)))
                                                  return buckets[v];
                                                return -1;
                                              }
```

对于右侧改进版本的 `mapToBucket`，编译器很可能会生成一个单个分支指令，以防止对 `buckets` 数组进行越界访问。这个函数的典型热路径将执行未采取的分支和一个加载指令。由于我们期望大多数输入值都落在 `buckets` 数组覆盖的范围内，CPU 分支预测器将很好地预测这个分支。查找速度也很快，因为 `buckets` 数组很小且很可能位于 L1-d 缓存中。

如果我们需要映射一个更大范围的值，比如 `[0-1M)`，分配一个非常大的数组是不现实的。在这种情况下，我们可以使用区间映射数据结构，它们可以使用更少的内存来实现这个目标，但查找复杂度是对数级的。读者可以在 [Boost](https://www.boost.org/doc/libs/1_65_0/libs/icl/doc/html/boost/icl/interval_map.html)[^2] 和 [LLVM](https://llvm.org/doxygen/IntervalMap_8h_source.html)[^3] 找到现有的区间映射容器实现。

[^2]: C++ Boost `interval_map` - [https://www.boost.org/doc/libs/1_65_0/libs/icl/doc/html/boost/icl/interval_map.html](https://www.boost.org/doc/libs/1_65_0/libs/icl/doc/html/boost/icl/interval_map.html)
[^3]: LLVM's `IntervalMap` - [https://llvm.org/doxygen/IntervalMap_8h_source.html](https://llvm.org/doxygen/IntervalMap_8h_source.html)

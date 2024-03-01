
## 数据流依赖

当程序语句引用前面语句的数据时，我们称这两个语句之间存在数据依赖性。有时人们也使用“依赖链”或“数据流依赖”等术语。我们最熟悉的例子如图 [@fig:LinkedListChasing](#LinkedListChasing) 所示。要访问节点 `N+1`，我们应该首先取消引用指针 `N->next` 的引用。对于右边的循环，这是一个递归的数据依赖性，这意味着它跨越了循环的多个迭代。基本上，遍历一个链表是一个非常长的依赖链。

![遍历链表时的数据依赖性.](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/computation-opts/LinkedListChasing.png)<div id="LinkedListChasing"></div>


传统程序是在假设顺序执行模型的情况下编写的。在这个模型下，指令一个接一个地执行，原子地按照程序指定的顺序执行。然而，正如我们已经知道的，现代 CPU 不是这样构建的。它们被设计成乱序执行指令，并行执行，并以最大限度利用可用执行单元的方式执行。

当出现长数据依赖性时，处理器被迫以顺序执行代码，只利用了其全部能力的一部分。长依赖链阻碍了并行性，这违背了现代超标量 CPU 的主要优势。例如，指针追逐不能从 OOO 执行中获益，因此将以顺序 CPU 的速度运行。正如我们将在本节看到的那样，依赖链是性能瓶颈的主要来源。

您无法消除数据依赖性，它们是程序的基本属性。任何程序都接受输入来计算一些东西。事实上，人们已经开发了技术来发现语句之间的数据依赖性并构建数据流图。这称为依赖性分析，更适合编译器开发人员，而不是性能工程师。我们不希望为整个程序构建数据流图。相反，我们想在一段热代码（循环或函数）中找到一个关键的依赖链。

您可能会问：“如果不能摆脱依赖链，您可以做什么？”。嗯，有时这会成为性能的限制因素，不幸的是您将不得不忍受它。在本书的最后一章，我们将讨论硬件中打破依赖链的一种可能解决方案，称为值预测。现在，您应该寻找打破不必要的数据依赖链或使其执行重叠的方法。一个这样的例子显示在 [@lst:DepChain](#DepChain) 中。与其他一些情况类似，我们在左边展示了源代码，右边是相应的 ARM 汇编代码。此外，这个代码示例包含在 Performance Ninja 的 Github 存储库中，因此您可以自己尝试一下。

这个小程序模拟了随机粒子运动。我们有 1000 个粒子在 2D 表面上运动，没有约束，这意味着它们可以离它们的起始位置尽可能远。每个粒子由其在 2D 表面上的 x 和 y 坐标以及速度定义。初始 x 和 y 坐标在范围 [-1000,1000] 内，速度在范围 [0;1] 内，不会改变。程序模拟每个粒子 1000 个运动步长。对于每个步骤，我们使用随机数生成器 (RNG) 生成一个角度，该角度设置粒子的运动方向。然后，我们相应地调整粒子的坐标。

考虑到手头的任务，您决定自己编写 RNG、正弦和余弦函数，以牺牲一些精度使其尽可能快。毕竟，这是随机运动，所以这是一个不错的权衡。您选择中等质量的 `XorShift` RNG，因为它只有 3 个移位和 3 个异或操作。还有什么更简单的？另外，您很快搜索了网络，使用多项式找到了正弦和余弦近似值，既准确又快速。

让我们快速检查一下生成的 ARM 汇编代码：
* 前三个 `eor` 指令与 `lsl` 或 `lsr` 组合对应于 `XorShift32::gen()` 函数。
* 接下来的 `ucvtf` 和 `fmul` 用于将角度从度转换为弧度（代码第 35 行）。
* 正弦和余弦函数都具有两个 `fmul` 和一个 `fmadd` 操作。余弦还具有附加的 `fadd`。
* 最后，我们再有一对 `fmadd` 来分别计算 x 和 y，以及 `stp` 指令将坐标对存储回原处。

使用 Clang-17 C++ 编译器编译了代码并在 Mac mini (Apple M1, 2020) 上运行。期望这段代码“飞起来”，但是有一个非常讨厌的性能问题使程序变慢。不提前阅读文本，你能在代码中找到一个递归依赖链吗？

代码清单:二维表面上的随机粒子运动 <div id="DepChain"></div>

```cpp
struct Particle {                                    │
  float x; float y; float velocity;                  │
};                                                   │
                                                     │
class XorShift32 {                                   │
  uint32_t val;                                      │
public:                                              │
  XorShift32 (uint32_t seed) : val(seed) {}          │
  uint32_t gen() {                                   │
    val ^= (val << 13);                              │
    val ^= (val >> 17);                              │
    val ^= (val << 5);                               │
    return val;                                      │ .loop:
  }                                                  │   eor    w0, w0, w0, lsl #13
};                                                   │   eor    w0, w0, w0, lsr #17
                                                     │   eor    w0, w0, w0, lsl #5
static float sine(float x) {                         │   ucvtf  s1, w0
  const float B = 4 / PI_F;                          │   fmov   s2, w9
  const float C = -4 / ( PI_F * PI_F);               │   fmul   s2, s1, s2
  return B * x + C * x * std::abs(x);                │   fmov   s3, w10
}                                                    │   fadd   s3, s2, s3
static float cosine(float x) {                       │   fmov   s4, w11
  return sine(x + (PI_F / 2));                       │   fmul   s5, s3, s3
}                                                    │   fmov   s6, w12
                                                     │   fmul   s5, s5, s6
/* Map degrees [0;UINT32_MAX) to radians [0;2*pi)*/  │   fmadd  s3, s3, s4, s5
float DEGREE_TO_RADIAN = (2 * PI_D) / UINT32_MAX;    │   ldp    s6, s4, [x1, #0x4]
                                                     │   ldr    s5, [x1]
void particleMotion(vector<Particle> &particles,     │   fmadd  s3, s3, s4, s5
                    uint32_t seed) {                 │   fmov   s5, w13
 XorShift32 rng(seed);                               │   fmul   s5, s1, s5
 for (int i = 0; i < STEPS; i++)                     │   fmul   s2, s5, s2
  for (auto &p : particles) {                        │   fmadd  s1, s1, s0, s2
   uint32_t angle = rng.gen();                       │   fmadd  s1, s1, s4, s6
   float angle_rad = angle * DEGREE_TO_RADIAN;       │   stp    s3, s1, [x1], #0xc
   p.x += cosine(angle_rad) * p.velocity;            │   cmp    x1, x16
   p.y += sine(angle_rad) * p.velocity;              │   b.ne   .loop
  }                                                  │
}                                                    │
```

恭喜您找到了它！存在一个关于 `XorShift32::val` 的循环依赖。要生成下一个随机数，生成器必须首先生成前一个数字。`gen()` 方法的下一个调用将基于前一个数字生成数字。图 [@fig:DepChain](#DepChain) 直观地显示了有问题的循环进位依赖。请注意，计算粒子坐标的代码（将角度转换为弧度，正弦，余弦，乘以速度）会在相应的随机数准备好后立即开始执行，但不会更早。

![在 [@lst:DepChain](#DepChain) 中依赖执行的可视化](https://raw.githubusercontent.com/dendibakh/perf-book/main/img/computation-opts/DepChain.png)<div id="DepChain"></div>

每个粒子坐标的计算代码彼此独立，因此向左拉伸它们以更多地重叠它们的执行可能会有益。您可能想知道：“但是这三个（或六个）指令如何拖慢整个循环？”。确实，循环中还有许多其他“繁重”指令，例如 `fmul` 和 `fmadd`。然而，它们不在关键路径上，因此可以与其他指令并行执行。并且由于现代 CPU 非常宽，它们将同时执行来自多个迭代的指令。这允许 OOO 引擎在循环的不同迭代中有效地找到并行性（独立指令）。

让我们做一些粗略的计算。[^1] 每个 `eor` 和 `lsl` 指令的延迟为 2 个周期，一个周期用于移位，一个周期用于异或。我们有三个依赖的 `eor + lsl` 对，因此生成下一个随机数需要 6 个周期。这是我们这个循环的绝对最小值，我们不能以每迭代 6 个周期以上的速度运行。后续代码至少需要 20 个周期延迟才能完成所有 `fmul` 和 `fmadd` 指令。但这没关系，因为它们不在关键路径上。重要的是这些指令的吞吐量。经验法则：如果一条指令处于关键路径上，请查看其延迟；如果它不在关键路径上，请查看其吞吐量。在每个循环迭代中，我们有 5 个 `fmul` 和 4 个 `fmadd` 指令，它们都在同一组执行单元上执行。M1 处理器可以每周期运行 4 条这种类型的指令，因此发出所有 `fmul` 和 `fmadd` 指令至少需要 `9/4 = 2.25` 个周期。因此，我们有两个性能限制：第一个由软件强制（每个迭代 6 个周期，由于依赖链），第二个由硬件强制（每个迭代 2.25 个周期，由于执行单元的吞吐量）。现在我们受第一个限制约束，但我们可以尝试打破依赖链以接近第二个限制。

解决这个问题的一种方法是使用额外的 RNG 对象，使其一个为循环的偶数迭代提供数据，另一个为奇数迭代提供数据，如 [@lst:DepChainFixed](#DepChainFixed) 所示。请注意，我们还手动展开循环。现在我们有两个独立的依赖链，可以并行执行。有人可能会说这改变了程序的功能，但用户无法分辨，因为粒子的运动是随机的。另一种解决方案是选择一个内部依赖链更少的 RNG。

代码清单:二维表面上的随机粒子运动 <div id="DepChainFixed"></div>

```cpp
void particleMotion(vector<Particle> &particles, 
                    uint32_t seed1, uint32_t seed2) {
  XorShift32 rng1(seed1);
  XorShift32 rng2(seed2);
  for (int i = 0; i < STEPS; i++) {
    for (int j = 0; j + 1 < particles.size(); j += 2) {
      uint32_t angle1 = rng1.gen();
      float angle_rad1 = angle1 * DEGREE_TO_RADIAN;
      particles[j].x += cosine(angle_rad1) * particles[j].velocity;
      particles[j].y += sine(angle_rad1)   * particles[j].velocity;
      uint32_t angle2 = rng2.gen();
      float angle_rad2 = angle2 * DEGREE_TO_RADIAN;
      particles[j+1].x += cosine(angle_rad2) * particles[j+1].velocity;
      particles[j+1].y += sine(angle_rad2)   * particles[j+1].velocity;
    }
    // remainder (not shown)
  }
}
```

完成此转换后，编译器开始自动矢量化循环主体，即它将两个链粘合在一起并使用 SIMD 指令并行处理它们。为了隔离打破依赖链的影响，我们禁用了编译器矢量化。

为了测量改变的影响，我们运行了“之前”和“之后”版本，观察到运行时间从每个迭代 19 毫秒降至每个迭代 10 毫秒。这几乎是 2 倍的加速。IPC 也从 4.0 上升到 7.1。为了尽职尽责，我们还测量了其他指标，以确保性能不会因其他原因意外提升。在原始代码中，MPKI 为 0.01，BranchMispredRate 为 0.2%，这意味着程序最初没有遭受缓存未命中或分支预测错误。这里还有另一个数据点：在英特尔的 Alderlake 系统上运行相同的代码时，它显示了 74% 的 Retiring 和 24% 的 Core Bound，这证实了性能受计算限制。

通过一些额外的更改，您可以将此解决方案通用化，以拥有您想要的任意数量的依赖链。对于 M1 处理器，测量结果表明拥有 2 个依赖链足以非常接近硬件限制。拥有超过 2 个链路的性能提升可以忽略不计。然而，一个趋势是 CPU 变得越来越宽，即它们越来越能够并行运行多个依赖链。这意味着未来的处理器可以受益于拥有超过 2 个依赖链。与往常一样，您应该测量并找到您的代码将在其上运行的平台的最佳点。

有时仅打破依赖链还不够。想象一下，您没有一个简单的 RNG，而是一个非常复杂的加密算法，它长达 10'000 个指令。因此，现在我们不再是一个非常短的 6 个指令依赖链，而是有 10'000 个指令位于关键路径上。您立即进行上述相同的更改，期待获得 2 倍的加速。只会看到性能稍有提升。发生了什么？

这里的问题是 CPU 无法“看到”第二个依赖链开始执行它。回想一下第 3 章，预留站 (RS) 的容量不足以提前看到 10'000 条指令，因为它比这小得多。因此，CPU 将无法重叠执行两个依赖链。为了修复它，我们需要*交错*这两个依赖链。使用这种方法，您需要更改代码，以便 RNG 对象同时生成两个数字，函数 `gen()` 中的 *每个* 语句都重复并交错。即使编译器内联所有代码并且可以清楚地看到两个链，它也不会自动交错它们，因此您需要小心这一点。您在执行此操作时可能遇到的另一个限制是寄存器压力。并行运行多个依赖链需要保持更多状态，因此需要更多寄存器。如果您用完寄存器，编译器会将它们溢出到堆栈，从而减慢程序速度。

作为结束时的思考，我们想强调找到关键依赖链的重要性。这并不总是容易的，但要知道您的循环、函数或代码段的关键路径上是什么至关重要。否则，您可能会发现自己在修复次要问题，而这些问题几乎没有影响。

[^1]:苹果公司没有公布他们产品的指令延迟和吞吐量，但有一些实验可以说明这一点，这里有一个这样的研究:[https://dougallj.github.io/applecpu/firestorm-simd.html](https://dougallj.github.io/applecpu/firestorm-simd.html)。由于这是非官方的数据来源，你应该有所保留。

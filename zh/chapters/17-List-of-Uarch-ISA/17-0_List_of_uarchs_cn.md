[TODO]:在下面的表格中添加边框线

## 主要 CPU 微架构列表 {.unnumbered}

\markright{List of the Major CPU Microarchitectures}

下表列出了来自英特尔、AMD 和基于 ARM 的供应商的最新 ISA 和微架构。当然，这里并未列出所有设计。我们只包含了我们在书中参考的架构，或者代表平台演进中重大转变的架构。

---------------------------------------------------------------
| 名称        | 三字母缩写 | 发布年份 | 支持的 ISA                                              | 支持的客户端/服务器芯片 |
| ------------- | -------- | -------- | ---------------------------------------------------------- | -------------------------- |
| Nehalem     | NHM     | 2008     | SSE4.2                                                  | Core i3/i5/i7                |
| Sandy Bridge | SNB     | 2011     | AVX                                                    | Core i3/i5/i7                |
| Haswell     | HSW     | 2013     | AVX2                                                   | Core i3/i5/i7                |
| Skylake     | SKL     | 2015     | AVX2 / AVX512                                         | Core i3/i5/i7, Xeon Scalable |
| Sunny Cove | SNC     | 2019     | AVX512                                                  | Ice Lake, Tiger Lake        |
| Golden Cove | GLC     | 2021     | AVX2 / AVX512                                         | Alder Lake                 |
| Redwood Cove| RWC     | 2023     | AVX2 / AVX512                                         | Raptor Lake                 |

表：最近的英特尔酷睿微架构列表。 {#tbl:IntelUarchs}

----------------------------------------------
| 名称 | 发布年份 | 支持的 ISA |
| -------- | -------- | -------- |
| Streamroller | 2014 | AVX |
| Excavator | 2015 | AVX2 |
| Zen | 2017 | AVX2 |
| Zen2 | 2019 | AVX2 |
| Zen3 | 2020 | AVX2 |
| Zen4 | 2022 | AVX512 |

表：最近的 AMD 微架构列表。{#tbl:AMDUarchs}

------------------------------------------------------------------
| ISA | ISA 发布年份 | ARM 微架构 (最新) | 第三方微架构 |
| ------------ | -------- | -------- | -------- |
| ARMv8-A | 2011 | Cortex-A73 | Apple A7-A10; Qualcomm Kryo; Samsung M1/M2/M3 |
| ARMv8.2-A | 2016 | Neoverse N1; Cortex-X1 | Apple A11; Samsung M4; Ampere Altra |
| ARMv8.4-A | 2017 | Neoverse V1 | AWS Graviton3; Apple A13, M1 |
| ARMv9.0-A (仅限 64 位) | 2018 | Neoverse N2; Neoverse V2; Cortex X3 | Microsoft Cobalt 100; NVIDIA Grace |
| ARMv8.6-A (仅限 64 位) | 2019 | --- | Apple A15, A16, M2, M3 |
| ARMv9.2-A | 2020 | Cortex X4 | --- |

表：最近的 ARM ISA 及其自身和第三方实现。{#tbl:ARMUarchs}

\bibliography{biblio}
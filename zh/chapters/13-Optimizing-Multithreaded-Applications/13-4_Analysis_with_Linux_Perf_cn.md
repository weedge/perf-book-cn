## 使用 Linux Perf 进行分析

Linux 的 `perf` 工具可以对应用程序可能产生的所有线程进行性能分析。它有 `-s` 选项，可以记录每个线程的事件计数。使用此选项，在报告的末尾，`perf` 列出了所有线程 ID 以及每个线程收集的样本数：

```bash
$ perf record -s ./x264 -o /dev/null --slow --threads 8 Bosphorus_1920x1080_120fps_420_8bit_YUV.y4m
$ perf report -n -T
...
#  PID   TID   cycles:ppp
  6966  6976  41570283106
  6966  6971  25991235047
  6966  6969  20251062678
  6966  6975  17598710694
  6966  6970  27688808973
  6966  6972  23739208014
  6966  6973  20901059568
  6966  6968  18508542853
  6966  6967     48399587
  6966  6966   2464885318
```

要为特定的软件线程过滤样本，可以使用 `--tid` 选项：

```bash
$ perf report -T --tid 6976 -n
# Overhead  Samples  Shared Object  Symbol
# ........  .......  .............  ...................................
     7.17%   19877       x264       get_ref_avx2
     7.06%   19078       x264       x264_8_me_search_ref
     6.34%   18367       x264       refine_subpel
     5.34%   15690       x264       x264_8_pixel_satd_8x8_internal_avx2
     4.55%   11703       x264       x264_8_pixel_avg2_w16_sse2
     3.83%   11646       x264       x264_8_pixel_avg2_w8_mmx2
```

Linux 的 `perf` 也自动提供了我们在 [@sec:secMT_metrics] 中讨论的一些指标：

```bash
$ perf stat ./x264 -o /dev/null --slow --threads 8 Bosphorus_1920x1080_120fps_420_8bit_YUV.y4m
         86,720.71 msec task-clock        #    5.701 CPUs utilized
            28,386      context-switches  #    0.327 K/sec
             7,375      cpu-migrations    #    0.085 K/sec
            38,174      page-faults       #    0.440 K/sec
   299,884,445,581      cycles            #    3.458 GHz
   436,045,473,289      instructions      #    1.45  insn per cycle
    32,281,697,229      branches          #  372.249 M/sec
       971,433,345      branch-misses     #    3.01% of all branches
```

### 查找开销大的锁

要使用 Linux 的 `perf` 找到最有争议的同步对象，需要对调度程序上下文切换进行采样（`sched:sched_switch`），这是一个内核事件，因此需要 root 访问权限：

```bash
$ sudo perf record -s -e sched:sched_switch -g --call-graph dwarf -- ./x264 -o /dev/null --slow --threads 8 Bosphorus_1920x1080_120fps_420_8bit_YUV.y4m
$ sudo perf report -n --stdio -T --sort=overhead,prev_comm,prev_pid --no-call-graph -F overhead,sample
# Samples: 27K of event 'sched:sched_switch'
# Event count (approx.): 27327
# Overhead       Samples         prev_comm    prev_pid
# ........  ............  ................  ..........
    15.43%          4217              x264        2973
    14.71%          4019              x264        2972
    13.35%          3647              x264        2976
    11.37%          3107              x264        2975
    10.67%          2916              x264        2970
    10.41%          2844              x264        2971
     9.69%          2649              x264        2974
     6.87%          1876              x264        2969
     4.10%          1120              x264        2967
     2.66%           727              x264        2968
     0.75%           205              x264        2977
```

上面的输出显示了哪些线程最频繁地被切换出执行。请注意，我们还收集了调用堆栈（`--call-graph dwarf`，见 [[@sec:secCollectCallStacks](../5-Performance-Analysis-Approaches/5-5_Sampling_cn.md#sec:secCollectCallStacks)]），因为我们需要用它来分析导致昂贵同步事件的路径：

```bash
$ sudo perf report -n --stdio -T --sort=overhead,symbol -F overhead,sample -G
# Overhead       Samples  Symbol
# ........  ............  ...........................................
   100.00%         27327  [k] __sched_text_start                     
   |
   |--95.25%--0xffffffffffffffff
   |  |
   |  |--86.23%--x264_8_macroblock_analyse
   |  |  |
   |  |   --84.50%--mb_analyse_init (inlined)
   |  |     |
   |  |      --84.39%--x264_8_frame_cond_wait
   |  |        |
   |  |         --84.11%--__pthread_cond_wait (inlined)
   |  |                   __pthread_cond_wait_common (inlined)
   |  |                   |
   |  |                    --83.88%--futex_wait_cancelable (inlined)
   |  |                              entry_SYSCALL_64
   |  |                              do_syscall_64
   |  |                              __x64_sys_futex
   |  |                              do_futex
   |  |                              futex_wait
   |  |                              futex_wait_queue_me
   |  |                              schedule
   |  |                             

 __sched_text_start
   ...
```

上面的列表显示了导致等待条件变量 (`__pthread_cond_wait`) 和后续上下文切换的最频繁路径。这条路径是 `x264_8_macroblock_analyse -> mb_analyse_init -> x264_8_frame_cond_wait`。从这个输出中，我们可以得知 84% 的上下文切换都是由线程在 `x264_8_frame_cond_wait` 中等待条件变量引起的。
## 利用 eBPF 和 GAPP 进行分析 {#sec:secEBPF}

Linux 支持各种线程同步原语 - 互斥锁、信号量、条件变量等。内核通过 `futex` 系统调用支持这些线程原语。因此，通过追踪内核中 `futex` 系统调用的执行，同时从涉及的线程中收集有用的元数据，可以更轻松地识别争用瓶颈。Linux 提供了内核跟踪/分析工具，使之成为可能，其中 eBPF ([Extended Berkley Packet Filter](https://prototype-kernel.readthedocs.io/en/latest/bpf/)[^22]) 的功能最为强大。

eBPF 基于内核中运行的沙箱虚拟机，允许在内核内安全高效地执行用户定义的程序。用户定义的程序可以用 C 语言编写，并由 BCC 编译器 ([https://github.com/iovisor/bcc](https://github.com/iovisor/bcc))[^23] 编译成 BPF 字节码，以便加载到内核虚拟机中。这些 BPF 程序可以编写成在某些内核事件执行时启动，并通过各种方式将原始或处理后的数据传回用户空间。

开源社区提供了许多用于通用目的的 eBPF 程序。其中一个工具是通用自动并行分析器 (Generic Automatic Parallel Profiler) (GAPP)，它有助于跟踪多线程争用问题。GAPP 使用 eBPF 通过对已识别的序列化瓶颈进行关键性排序来跟踪多线程应用程序的争用开销，收集被阻塞的线程和导致阻塞的线程的堆栈轨迹。GAPP 最好的方面是它不需要代码更改、昂贵的工具化或重新编译。GAPP 分析器的创建者能够确认已知的瓶颈，并且还揭示了 Parsec 3.0 Benchmark Suite ([https://parsec.cs.princeton.edu/index.htm](https://parsec.cs.princeton.edu/index.htm))[^24] 和一些大型开源项目中以前未报告的新瓶颈。

[^22]: eBPF 文档 - [https://prototype-kernel.readthedocs.io/en/latest/bpf/](https://prototype-kernel.readthedocs.io/en/latest/bpf/)
[^23]: BCC 编译器 - [https://github.com/iovisor/bcc](https://github.com/iovisor/bcc)
[^24]: Parsec 3.0 基准测试套件 - [https://parsec.cs.princeton.edu/index.htm](https://parsec.cs.princeton.edu/index.htm)

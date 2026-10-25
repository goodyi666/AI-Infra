"""GPU 基准测试练习：比较提交耗时、同步耗时和 CUDA Event 耗时。

已激活 pytorch 环境时运行：
    python -X utf8 benchmark_pytorch.py

未激活环境时运行：
    conda run --no-capture-output -n pytorch python -X utf8 benchmark_pytorch.py

Windows 上部分 Conda 版本默认捕获输出时会错误解码中文，使用上述方式避免乱码。
"""

from statistics import median
from time import perf_counter

import torch


def benchmark_gpu(fn, warmup=5, repeat=20, synchronize=True):
    """返回耗时中位数，单位为毫秒。此函数仅用于 CUDA 任务。"""
    for _ in range(warmup):
        fn()
    torch.cuda.synchronize()  # 先排除预热期间尚未完成的工作

    samples = []
    for _ in range(repeat):
        if synchronize:
            torch.cuda.synchronize()
        start = perf_counter()
        fn()
        if synchronize:
            torch.cuda.synchronize()  # 结束计时前等待 GPU 完成
        samples.append((perf_counter() - start) * 1000)

    # 不同步的对照组也要在最后清空待完成工作，但不把它计入样本。
    torch.cuda.synchronize()
    return median(samples)


def benchmark_events(fn, warmup=5, repeat=20):
    """返回同一 CUDA 流上两个 Event 之间的耗时中位数，单位为毫秒。"""
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    torch.cuda.synchronize()

    samples = []
    for index in range(warmup + repeat):
        start.record()
        fn()
        end.record()
        end.synchronize()  # 等待结束标记完成后，才能读取时间差
        if index >= warmup:
            samples.append(start.elapsed_time(end))
    return median(samples)


def main():
    if not torch.cuda.is_available():
        raise RuntimeError("本例需要支持 CUDA 的 PyTorch 环境，请使用 pytorch 环境运行。")

    torch.manual_seed(0)
    size = 2048
    # 输入和输出缓冲区在计时前准备好，每次使用相同形状和数据。
    x = torch.randn(size, size, device="cuda")
    y = torch.randn(size, size, device="cuda")
    out = torch.empty_like(x)

    def matmul():
        torch.mm(x, y, out=out)

    print(f"PyTorch：{torch.__version__}")
    print(f"GPU：{torch.cuda.get_device_name()}")
    print(f"矩阵形状：{size} × {size}，float32")
    print("每组预热 5 次，正式采样 20 次，报告中位数。")

    launch_ms = benchmark_gpu(matmul, synchronize=False)
    synchronized_ms = benchmark_gpu(matmul, synchronize=True)
    event_ms = benchmark_events(matmul)

    print(f"不等待完成的 CPU 计时：{launch_ms:.3f} ms")
    print(f"等待 GPU 完成的 CPU 计时：{synchronized_ms:.3f} ms")
    print(f"CUDA Event 计时：{event_ms:.3f} ms")
    print("三者测量边界不同，不应把它们的比值当成算法加速比。")


if __name__ == "__main__":
    main()

"""asyncio 整理版：比较三种等待方式。请求和读文件均为模拟操作。"""

import asyncio
from time import perf_counter


async def fetch_url(url: str) -> str:
    print(f"开始模拟请求：{url}")
    # 在计时等待期间挂起当前任务，事件循环可以推进其他就绪任务。
    await asyncio.sleep(1)
    print("模拟请求完成")
    return "url_content"


async def read_file(filepath: str) -> str:
    print(f"开始模拟读取：{filepath}")
    await asyncio.sleep(1)
    print("模拟读取完成")
    return "file_content"


async def sequential(url: str, filepath: str) -> list[str]:
    # 第一个协程完成后，才创建并运行第二个协程：总等待约 2 秒。
    fetch_result = await fetch_url(url)
    read_result = await read_file(filepath)
    return [fetch_result, read_result]


async def concurrent_gather(url: str, filepath: str) -> list[str]:
    # gather 把两个协程安排为任务，重叠等待：总等待约 1 秒。
    results = await asyncio.gather(fetch_url(url), read_file(filepath))
    return results


async def concurrent_tasks(url: str, filepath: str) -> list[str]:
    # create_task 需要正在运行的事件循环，这里位于 async 函数中。
    task1 = asyncio.create_task(fetch_url(url))
    task2 = asyncio.create_task(read_file(filepath))

    # 两个任务都已安排。依次 await 它们，不会让执行退回串行。
    fetch_result = await task1
    read_result = await task2
    return [fetch_result, read_result]


async def main() -> None:
    url = "https://www.example.com"
    filepath = "example.txt"
    cases = [
        ("连续 await 尚未启动的协程", sequential),
        ("使用 gather 并发", concurrent_gather),
        ("先创建 Task，再依次 await", concurrent_tasks),
    ]

    # 三组实验依次执行，每组内部是否并发取决于对应写法。
    for label, run_case in cases:
        print(f"\n--- {label} ---")
        start = perf_counter()
        results = await run_case(url, filepath)
        elapsed = perf_counter() - start
        print(f"结果：{results}")
        print(f"耗时：{elapsed:.3f} 秒")


if __name__ == "__main__":
    # 先由 run 建立事件循环，再在其中执行 main 和各个练习任务。
    asyncio.run(main())

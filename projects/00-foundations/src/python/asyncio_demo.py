import asyncio


def worker(name):
    print(name)


async def worker_async(name):
    print(name)


async def main():
    # 调用协程函数得到协程对象，用 await 运行并等待它完成。
    await worker_async('b')
    await worker_async('c')


if __name__ == '__main__':
    worker('a')
    # 普通脚本使用 asyncio.run 启动事件循环并运行入口协程。
    asyncio.run(main())

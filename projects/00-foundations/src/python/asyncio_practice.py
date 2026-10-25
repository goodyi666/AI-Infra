# 协程：是可以暂停运行和恢复运行的函数
# 事件循环：用来调度协程执行，掌握控制权。循环往复做三件事：
    # 1.检查协程：拿到控制权后，检查有没有可以执行的协程
    # 2.让出控制：将控制权传递给可以执行的协程
    # 3.等待协程：等当前协程暂停或者运行完成放开控制权给自己

""" 
import asyncio

async def coroutine_function():
    return 'This is a coroutine function'

print(coroutine_function()) #调用协程函数不会执行里面的代码，而是返回一个协程对象，运行协程对象时才会执行里面的代码
 """
# 1. 定义协程函数
# 2. 包装协程为任务
# 3. 建立事件循环
from time import sleep, perf_counter
import asyncio
""" 
def fetch_url(url):
    print('Fetching the URL')
    sleep(1)
    print('Finished fetching the URL')
    return 'url_content'

def read_file(filepath):
    print('Fetching the file')
    sleep(1)
    print('Finished fetching the file')
    return 'file_content'

def main():
    url = 'https://www.example.com'
    filepath = 'example.txt'
    fetch_result=fetch_url(url)
    read_result=read_file(filepath)

if __name__ == '__main__':
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print(f'Total execution time: {end_time-start_time} seconds.')
 """

async def fetch_url(url):
    print('Fetching the URL')
    await asyncio.sleep(1) # await 关键字：暂停当前协程的执行，等待其他协程运行，直到被等待的协程运行完成后再恢复当前协程的执行
    print('Finished fetching the URL')
    return 'url_content'

async def read_file(filepath):
    print('Fetching the file')
    await asyncio.sleep(1)
    print('Finished fetching the file')
    return 'file_content'

async def main():
    url = 'https://www.example.com'
    filepath = 'example.txt'
    # 使用 asyncio.gather 并行运行协程
    results = await asyncio.gather(fetch_url(url), read_file(filepath)) # 并行运行协程，返回结果列表
    print(results) # 输出 ['url_content', 'file_content']
"""     # 手动创建任务并运行协程
    task1 = asyncio.create_task(fetch_url(url)) # 将协程包装为任务
    task2 = asyncio.create_task(read_file(filepath))

    fetch_result=await task1 # 等待任务完成并获取结果
    read_result=await task2 # 等待任务完成并获取结果 """
    
if __name__ == '__main__':
    start_time = perf_counter()
    asyncio.run(main()) # 建立事件循环并运行协程
    end_time = perf_counter()
    print(f'Total execution time: {end_time-start_time} seconds.')
    
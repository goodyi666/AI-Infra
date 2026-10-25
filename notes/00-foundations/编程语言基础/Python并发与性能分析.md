# Python 并发与性能分析

创建日期：2026-10-24

学习资料：[AIInfraGuide：Python 并发与性能分析](https://caomaolufei.github.io/AIInfraGuide/prerequisites/模块一-前置知识/第1章-编程语言基础/#3-python-并发与性能分析)

基础知识参考：[Python 学习笔记](Python学习笔记.md)。

## 01｜并发与并行

日期：2026-10-24

### 1. 区别：交替推进与同时执行

- **并发**：多个任务在同一时间段内推进，可以交替执行，单核也能实现。
- **并行**：多个任务在同一时刻真正执行，例如两个 CPU 核心各执行一个任务。

```text
并发的一种情况：
核心 1：A → B → A → B

并行的一种情况：
核心 1：A → A → A
核心 2：B → B → B
```

并发还能重叠等待时间。例如两个请求各等待约 1 秒：顺序执行约需 2 秒，并发执行在理想情况下接近 1 秒，不要求两段 Python 代码同时计算。

### 2. 根据瓶颈选择方式

| 任务类型 | 主要时间花在哪里 | 常见选择 |
| --- | --- | --- |
| I/O 密集 | 等待网络、文件等外部资源 | 线程或 asyncio，重叠等待时间 |
| Python CPU 密集 | 纯 Python 循环与计算 | 多进程或原生扩展 |
| 原生算子密集 | NumPy、PyTorch 等底层计算或 GPU 运算 | 先确认底层已有的线程池或 GPU 并行方式 |
| 大数据跨进程 | 数据传输、复制与对象重建 | 评估序列化成本，必要时使用共享内存 |

第四行强调的是数据搬运成本：多进程即使能并行计算，也可能被序列化、传输和反序列化拖慢。增加线程或进程不保证提速，需要测量实际瓶颈。

## 02｜CPython、进程、线程与 GIL

日期：2026-10-24

### 1. 先分清几个名字

| 概念 | 含义 |
| --- | --- |
| Python | 编程语言，规定语法与行为 |
| CPython | 最常用的 Python 解释器实现，主要用 C 编写 |
| 进程 | 运行中的程序实例，不同进程通常有独立内存空间 |
| 线程 | 进程内的执行路径，同一进程的线程共享内存 |
| GIL | CPython 用于保护解释器内部状态的全局解释器锁 |

普通 Python 程序通常在一个进程中运行一个解释器，主线程和工作线程使用这个解释器：

```text
一个 Python 进程
└─ 一个 CPython 解释器实例（启用 GIL）
   ├─ 主线程
   ├─ 工作线程 A
   └─ 工作线程 B
```

**创建线程不会自动创建新解释器。** 通常由解释器和扩展管理 GIL，普通 Python 代码不用手动申请它。

### 2. GIL 限制什么？

以下讨论常见的启用 GIL 的构建：**同一解释器中的线程，需要持有 GIL 才能执行 Python 字节码；同一时刻通常只有一个线程能执行这部分代码。**

```text
线程 A：持有 GIL，执行 Python 代码
线程 B：等待 GIL
    ↓ 之后可以交换
线程 A：等待 GIL
线程 B：持有 GIL，执行 Python 代码
```

所以，即使 CPU 有多个核心，把相同总量的纯 Python 计算交给两个线程，通常也不能获得两倍速度，甚至可能增加切换开销。

### 3. 没拿到 GIL，线程还能做什么？

| 工作 | 与 GIL 的关系 |
| --- | --- |
| 普通 Python 循环 | 执行字节码时需要持锁 |
| 常见阻塞 I/O | 等待期间通常释放 GIL，让其他线程执行 |
| 部分原生扩展计算 | 可释放 GIL，在底层执行；并非每种操作都会释放 |

例如 A 等网络响应时释放 GIL，B 就能执行自己的 Python 代码，因此线程适合 I/O 并发。GPU 上的并行计算也不要求 Python 为每个计算单元创建线程。

**GIL 不等于业务代码自动线程安全。** 多个线程共同修改数据时，仍可能需要 Lock 等同步机制。

### 4. 为什么多进程可以并行？有哪些例外？

- 常见多进程方式中，各进程运行自己的解释器，不争抢同一把 GIL，因此可以并行执行纯 Python 计算；但有创建进程和传递数据的成本。
- “一个进程一个解释器”是常见情况，不是强制规定。进程可以显式创建多个解释器；例如 Python 3.14 的 InterpreterPoolExecutor 为工作线程提供各自的解释器和 GIL。
- CPython 3.13 起提供可选 free-threaded 构建，可在禁用 GIL 时并行执行 Python 代码；部分扩展可能重新启用 GIL。不能只凭版本号判断实际行为。

参考：[线程与 GIL](https://docs.python.org/3.14/library/threading.html#gil-and-performance-considerations)、[多解释器线程池](https://docs.python.org/3.14/library/concurrent.futures.html#interpreterpoolexecutor)、[free-threaded 构建](https://docs.python.org/3.14/howto/free-threading-python.html)。

记住：**并发重在多个任务推进，并行重在同时执行；GIL 限制同一解释器中的 Python 执行，不包办 I/O、原生计算和业务数据同步。**

## 03｜线程：共享内存与锁

日期：2026-10-24

### 1. 原例：线程池并发请求

```python
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen

def fetch_size(url: str) -> int:
    with urlopen(url, timeout=10) as response:
        return len(response.read())  # 读取完整响应，返回字节数

urls = ["https://example.com"] * 4  # 四个相同地址，分别请求四次
with ThreadPoolExecutor(max_workers=4) as pool:
    sizes = list(pool.map(fetch_size, urls))
```

- `max_workers=4`：最多使用 4 个工作线程，由线程池安排任务、复用线程。
- `pool.map(fetch_size, urls)`：把每个 URL 分别传给 fetch_size，多个调用可以并发进行。这里传入函数本身，不写 `fetch_size()`。
- `list(...)`：获取全部结果并收集成列表；**结果按输入顺序排列，不按完成顺序排列**。获取某项结果时，对应任务的异常也会向外抛出。
- 退出线程池的 with 时，等待已提交任务结束并清理资源。fetch_size 内的 with 则负责关闭响应对象，包括 return 离开时。
- `timeout=10` 是连接等阻塞网络操作的超时参数，不保证整个函数总耗时严格小于 10 秒。

网络等待期间通常释放 GIL，其他线程可以推进请求，所以线程适合这类 I/O 任务。sizes 保存的是响应内容的**字节数**，不是文字字符数。

### 2. 共享内存为什么会有风险？

线程可以访问同一份对象，通常无需像普通跨进程传输那样序列化、复制并重建对象，但共享修改需要协调。

例如，计数器加一在逻辑上涉及：**读取旧值 → 计算新值 → 写回**。潜在交错如下：

```text
counter 初始为 0
A 读到 0，B 也读到 0
A 算出 1 并写回，B 也算出 1 并写回
最终得到 1，而不是预期的 2
```

这种正确性依赖线程操作交错顺序的问题叫竞态。这里整数本身不可变，共享修改的是 counter 这个模块变量的绑定。

**GIL 不会自动把你定义的一组业务操作保护为不可分割的整体。** 某个版本中简单的 `counter += 1` 可能不易复现上述交错，也不能当作跨版本、跨对象实现的原子性保证。

### 3. 原例：用 Lock 保护计数器

```python
from threading import Lock

lock = Lock()  # 相关线程共用同一把锁
counter = 0

def increment() -> None:
    global counter  # 修改模块级绑定，而非创建局部变量
    with lock:
        counter += 1
```

- `global counter`：声明这里要修改模块变量。因为 `+=` 既读又赋值，不写 global 会被当作局部变量，读取时可能报 UnboundLocalError。
- `with lock`：进入时获取锁，其他竞争者等待；退出时释放锁，包括异常退出。
- 持锁线程完成加一后，另一个线程才能进入同一临界区，读取更新后的值。
- **需要同步的相关访问必须遵守同一把锁。** 其他线程绕过锁操作共享数据，仍可能破坏正确性。

| 锁 | 保护范围 |
| --- | --- |
| GIL | 解释器内部状态及相应执行规则 |
| Lock | 程序明确指定的共享数据操作 |

### 4. 临界区尽可能小

临界区是需要加锁保护的代码段。只保护必要的共享数据更新，让无关工作继续并发：

```python
def fetch_and_count(url: str) -> int:
    global counter
    size = fetch_size(url)  # 网络请求放在锁外
    with lock:
        counter += 1       # 只保护共享计数器更新
    return size
```

如果把整个网络请求也放进同一把锁，其他线程就要等待它完成，难以重叠网络等待时间。

参考：[线程池](https://docs.python.org/3.14/library/concurrent.futures.html)、[Lock](https://docs.python.org/3.14/library/threading.html#lock-objects)。

记住：**线程方便共享数据，修改共享数据要同步；GIL 不代替业务锁，临界区只放必要操作。**

## 04｜多进程：绕开 GIL，但数据搬运有成本

日期：2026-10-25

### 1. 原例：进程池执行质数统计

```python
from concurrent.futures import ProcessPoolExecutor

def count_primes(limit: int) -> int:
    def is_prime(value: int) -> bool:
        if value < 2:
            return False
        return all(value % divisor for divisor in range(2, int(value**0.5) + 1))
    return sum(is_prime(value) for value in range(limit))

if __name__ == "__main__":
    with ProcessPoolExecutor() as pool:
        results = list(pool.map(count_primes, [50_000] * 4))
```

count_primes 统计小于 limit 的质数数量。例如小于 10 的质数为 2、3、5、7，所以 `count_primes(10)` 返回 4。

- `value % divisor` 是余数；为 0 表示能整除，不是质数。检查因子到平方根取整即可，range 的结束位置要加 1。
- `all(...)` 检查余数是否都非零，遇到零就停止；没有候选因子时返回 True，因此 2、3 会被正确判断。
- `sum(...)` 对判断结果求和，True 按 1、False 按 0 计算，得到质数数量。

### 2. pool.map 分配任务，list 收集结果

```python
result_iterator = pool.map(count_primes, [50_000] * 4)
results = list(result_iterator)
```

执行过程：输入序列的每个元素对应一次函数调用任务 → pool.map 提交任务 → 进程池自动安排工作进程执行 → 返回结果。

- `[50_000] * 4` 是四个相同的 50000，表示重复四次完整统计，**不是把一个区间拆成四份**。
- 工作进程会复用，一个进程可先后执行多个任务；四个任务不一定由四个不同进程执行。可用 `ProcessPoolExecutor(max_workers=4)` 限制最多四个工作进程。
- list 获取每个任务返回的整数，组成结果列表，**不是收集所有质数**。结果按输入顺序排列，取某项结果时若任务未完成就等待；任务异常会在获取对应结果时抛出。
- 例如 `list(pool.map(count_primes, [10] * 4))` 得到 `[4, 4, 4, 4]`。
- 退出 with 时，等待已提交任务结束并清理进程池资源。

### 3. 为什么需要 __main__ 判断？

Windows 默认使用 spawn：子进程启动新解释器，并重新加载主模块。创建进程池的入口必须保护起来，避免重新加载时再次启动进程池，触发重复启动及启动阶段错误。

```python
if __name__ == "__main__":
    # 这里只放程序入口中的启动操作
    ...
```

**保护入口不影响子进程执行分配到的任务。** count_primes 放在模块顶层，便于子进程导入；内部 is_prime 只在执行任务时创建，没有单独提交，因此这里可嵌套定义。练习时将完整程序保存为 .py 文件运行。

### 4. 为什么可能更快，也可能更慢？

常见多进程方式中，各进程使用自己的解释器和 GIL，可以在多个 CPU 核心上并行执行纯 Python 计算。普通全局变量不会因此自动跨进程共享。

主要成本包括：

- 创建进程、准备解释器环境，占用额外时间和内存。
- 参数及结果的序列化、传输、反序列化，以及可能的数据复制或内存映射。
- 任务调度、进程间通信与同步。

本例输入和输出都只是整数，搬运成本小；如果反复传大型数组，通信可能比计算更费时。共享内存可减少部分复制，但仍需管理访问与同步。

**增大任务粒度**就是让一个任务处理一批数据，减少过于细碎的任务提交和往返；同时保留足够任务供多个进程执行。任务太小，多进程开销可能超过收益。

### 5. CUDA 关联

原例仅做 CPU 计算。如果子进程要使用 CUDA，应遵循框架推荐的启动方式；父进程已初始化 CUDA 后随意 fork，可能继承不适合子进程使用的运行时状态，引发初始化错误。PyTorch 的 CUDA 子进程要求使用 spawn 或 forkserver 等合适方式，还需考虑各进程的上下文和显存成本。

参考：[进程池](https://docs.python.org/3.14/library/concurrent.futures.html#processpoolexecutor)、[安全导入主模块](https://docs.python.org/3.14/library/multiprocessing.html#safe-importing-of-main-module)、[PyTorch 多进程与 CUDA](https://docs.pytorch.org/docs/2.14/notes/multiprocessing.html#cuda-in-multiprocessing)。

记住：**map 提交任务，进程池分配执行，list 收集结果；多进程能并行计算，但要算上启动与数据搬运成本。**

## 05｜asyncio：协作式 I/O 并发

日期：2026-10-25

### 1. 核心概念

**asyncio 通常在一个事件循环线程中协调多个任务，通过重叠等待时间实现并发，不要求多个线程同时执行 Python 代码。**

| 名字 | 含义 |
| --- | --- |
| `async def` | 定义协程函数，调用后得到协程对象，函数体尚未执行 |
| 协程对象 | 可以被运行、在异步等待时挂起并恢复的对象 |
| Task | 交给事件循环调度的任务，驱动其中的协程执行 |
| `await` | 等待异步结果，需要等待时可挂起当前任务，让事件循环推进其他任务 |
| 事件循环 | 协调就绪任务、等待和恢复执行 |
| `asyncio.run(main())` | 普通脚本的异步入口，运行 main 并管理事件循环的收尾 |
| `asyncio.gather(...)` | 并发安排多个异步操作，并收集结果；传入协程时会将其安排为 Task |

async 不会自动创建线程；即使协程函数内部只有 print，单独调用它也不会执行函数体。

### 2. 原例与执行顺序

```python
import asyncio

async def worker(name: str, delay: float) -> str:
    await asyncio.sleep(delay)  # 当前任务暂停，模拟非阻塞 I/O 等待
    return name

async def main() -> None:
    results = await asyncio.gather(
        worker("a", 0.2),
        worker("b", 0.1),
    )
    print(results)  # ['a', 'b']

if __name__ == "__main__":
    asyncio.run(main())
```

1. asyncio.run 启动事件循环，运行 main。
2. gather 安排 a、b 两个任务，main 等待它们的结果。
3. a 开始等待 0.2 秒，b 开始等待 0.1 秒，两段等待重叠。
4. b 通常先完成，a 随后完成；都正常完成后，main 恢复并打印结果。

**gather 的结果按传入顺序排列，不按完成顺序排列。** 所以结果是 `['a', 'b']`，总耗时通常接近 0.2 秒加调度开销，而非 0.3 秒。

### 3. await 本身不保证并发

```python
async def main():
    a = await worker("a", 0.2)
    b = await worker("b", 0.1)
    print([a, b])
```

这里等 a 完成后才创建并运行 b，所以总等待时间接近 0.3 秒。gather 版本先安排两个任务，才允许它们重叠等待。

**await 负责等待；并发还需要把多个任务安排起来。** 也不是每个 await 都必然切换任务：等待结果已经就绪时，可能立即继续执行。

### 4. 不要阻塞事件循环

| 在协程内执行 | 效果 |
| --- | --- |
| `await asyncio.sleep(1)` | 暂停当前任务，事件循环可以推进其他任务 |
| `time.sleep(1)` | 阻塞事件循环线程，其他任务无法在该线程中推进 |
| 长时间纯 Python 循环 | 占住事件循环线程，不会因为 async 自动让出执行权 |

需要等待网络时使用异步库。已有普通阻塞函数，可以在协程内交给线程，例如前面的 fetch_size：

```python
size = await asyncio.to_thread(fetch_size, "https://example.com")
```

这里传入函数本身和参数，工作线程执行阻塞函数，事件循环等待期间仍能处理其他任务。纯 Python CPU 密集工作可考虑通过执行器接口衔接进程池。

### 5. 本次练习的易错点

练习文件：[asyncio_demo.py](../../../projects/00-foundations/src/python/asyncio_demo.py)。

| 写法或报错 | 原因与修正 |
| --- | --- |
| 普通 `worker('a')` | 立即执行函数，打印 a |
| 单独写 `worker_async('b')` | 只创建协程对象，未运行时不会打印 b；被丢弃时通常出现 was never awaited 警告 |
| `NameError: asyncio is not defined` | 使用前需要 `import asyncio` |
| `asyncio.rumtime(...)` | 拼写错误，应为 `asyncio.run(...)` |
| 文件命名为 `asyncio.py` | 可能遮蔽标准库 asyncio，练习文件使用 asyncio_demo.py 等名字 |

普通脚本入口用 `asyncio.run(main())`；在 async 函数内部可用 `await worker_async(...)`。连续 await 两个尚未启动的协程是顺序执行，asyncio.run 也不需要为每个子协程调用一次。

### 6. 练习：gather 与先创建 Task 的区别

原练习：[asyncio_practice.py](../../../projects/00-foundations/src/python/asyncio_practice.py)；保留原文件，另建 [整理对照版](../../../projects/00-foundations/src/python/asyncio_practice_reviewed.py)。

原例使用 gather 的主逻辑正确。需要修正的理解：

- 这里是**并发**，不是多个协程同时执行 Python 代码的并行。
- await 等待的是指定的异步结果，不是等待所有其他协程完成。本例 `await asyncio.sleep(1)` 等待的是计时结束，期间事件循环可推进其他任务。
- 当前 fetch_url、read_file 都用 sleep 模拟等待，没有真正请求 URL 或读取文件。
- 本脚本先定义协程函数，再由 `asyncio.run(main())` 建立事件循环；在 main 的执行过程中，gather 或 create_task 才安排任务。create_task 需要正在运行的事件循环。

以下写法都放在 async 函数内部；每个模拟操作等待约 1 秒：

```python
# 方式一：第一个完成后，才创建并运行第二个，约 2 秒
fetch_result = await fetch_url(url)
read_result = await read_file(filepath)
```

```python
# 方式二：gather 安排两个任务，重叠等待，约 1 秒
results = await asyncio.gather(fetch_url(url), read_file(filepath))
```

```python
# 方式三：先安排两个任务，再依次获取结果，仍然约 1 秒
task1 = asyncio.create_task(fetch_url(url))
task2 = asyncio.create_task(read_file(filepath))

fetch_result = await task1
read_result = await task2
```

**依次 await 已经安排的 Task，不会撤销它们的并发调度。** 等待 task1 时，task2 也能执行；轮到 await task2 时，它可能已完成。

整理版本机一次运行（2026-10-25），三种写法都得到 `['url_content', 'file_content']`：

| 写法 | 实测耗时 |
| --- | --- |
| 连续 await 尚未启动的协程 | 2.017 秒 |
| gather 并发 | 1.003 秒 |
| 先创建 Task，再依次 await | 1.001 秒 |

以上只演示模拟等待如何重叠，耗时包含调度开销；不能据此判断 gather 和 create_task 谁更快，也不是实际网络或磁盘性能测试。

参考：[协程与任务](https://docs.python.org/3.14/library/asyncio-task.html)、[避免阻塞事件循环](https://docs.python.org/3.14/library/asyncio-dev.html#concurrency-and-multithreading)。

记住：**async 定义协程函数，调用得到协程对象；事件循环负责调度，await 等待结果，gather 安排并发并收集结果。**

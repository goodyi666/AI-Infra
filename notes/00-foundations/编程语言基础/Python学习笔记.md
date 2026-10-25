# Python 学习笔记

## 01｜函数、对象引用与默认参数

日期：2026-10-23  
来源：[Python 函数定义解析（对话）](https://chatgpt.com/share/6adac129-11ec-83e8-8300-5536fe07372f)

### 1. 函数怎么定义？

```python
def add(a: int, b: int = 1) -> int:
    return a + b

print(add(3))     # 4，b 使用默认值
print(add(3, 5))  # 8
```

| 写法 | 含义 |
| --- | --- |
| `def add(...)` | 定义名为 add 的函数 |
| `a: int` | 参数 a，预期类型为整数 |
| `b: int = 1` | 参数 b，预期为整数，省略时使用 1 |
| `-> int` | 预期返回整数；箭头本身不会返回值 |
| 末尾的 `:` 和缩进 | 开始并划定函数体 |
| `return ...` | 结束函数并返回结果 |

类型注解可以省略，主要帮助阅读、编辑器提示和静态检查，**Python 本身不会因为注解而自动检查或转换类型**。上面的 `add("a", "b")` 仍能得到 `"ab"`。

`list[int]` 表示整数列表；`-> None` 表示预期返回 None。没有执行带值的 `return` 时，函数实际返回 `None`。

### 2. 修改对象 ≠ 给变量重新赋值

**变量名绑定到对象。传参时，形参与调用方变量最初引用同一个对象，不会自动复制对象。**

```python
def mutate(xs: list[int]) -> None:
    xs.append(1)  # 修改同一个列表

def rebind(xs: list[int]) -> None:
    xs = [1, 2]  # 只让局部名字 xs 绑定到新列表

data: list[int] = []
mutate(data)
print(data)  # [1]
rebind(data)
print(data)  # [1]
```

| 操作 | 效果 |
| --- | --- |
| `xs.append(1)` | 原地添加元素，调用方能看到变化 |
| `xs[0] = 100` | 原地替换元素（要求索引存在） |
| `xs[:] = [1, 2]` | 原地替换全部内容，仍是同一个列表 |
| `xs = [1, 2]` | 重新绑定局部名字，不改变调用方的绑定 |

如果函数返回了新列表，调用方需要用 `data = 函数(data)` 接住，才能让 data 指向新列表。

### 3. 为什么不建议用空列表作为默认参数？

**默认值在每次执行 `def`、创建函数时计算一次，省略参数的后续调用会复用它。**

```python
def collect_bad(x: int, result: list[int] = []) -> list[int]:
    result.append(x)
    return result

print(collect_bad(1))  # [1]
print(collect_bad(2))  # [1, 2]，复用上次的列表
```

这不是语法错误；问题是共享状态通常不符合“每次得到独立列表”的预期。

用 `None` 表示未提供列表，把创建列表的操作放进函数体：

```python
def collect(x: int, result: list[int] | None = None) -> list[int]:
    if result is None:
        result = []  # 每次执行到这里，都会创建新列表
    result.append(x)
    return result

print(collect(1))  # [1]
print(collect(2))  # [2]
```

- `list[int] | None`：预期为整数列表或 None；`= None` 才是设置默认值。
- `is None`：判断是否为 None；`if not result` 还会匹配空列表，含义不同。
- 默认的 None 也会复用；解决问题的关键是**在函数体内按需创建新列表**。
- 以上 `|` 联合类型写法使用 Python 3.10+。

### 4. 使用 None，仍可能修改传入的列表

```python
data = [10]
collect(20, data)
print(data)  # [10, 20]
```

主动传入列表时，result 仍引用它。若希望保留原列表，可在添加元素前先复制：

```python
result = [] if result is None else result.copy()
```

`copy()` 是浅拷贝：外层列表独立，嵌套的可变对象仍共享。

记住：**append 改对象，赋值改绑定；默认列表会复用，函数体里可以新建。**

## 02｜LEGB 与闭包

日期：2026-10-23；更新：2026-10-25

### 1. LEGB：名字去哪里找？

普通函数中读取名字时，按下面的顺序查找，找到就停止；都找不到则报 `NameError`。

| 顺序 | 作用域 | 含义 |
| --- | --- | --- |
| L：Local | 局部 | 当前函数的参数、局部变量 |
| E：Enclosing | 外层函数 | 在代码定义上包住当前函数的外层函数作用域 |
| G：Global | 模块 | 当前模块（通常是所在的 `.py` 文件）的顶层名字 |
| B：Builtins | 内置 | Python 提供的名字，如 `len`、`print` |

注意：**外层作用域看函数定义时的嵌套关系，不看是谁调用它。**

### 2. 闭包是什么？不加类型注解的例子

**闭包 = 内部函数 + 它引用的外层函数变量绑定。** 即使外层函数调用结束，内部函数仍能访问这些绑定。

外层返回内部函数是常见写法，不是必要条件，也可以把内部函数放进列表或作为回调传出。仅有函数嵌套、却不引用外层函数变量，并不会形成这里所说的闭包。

```python
def make_multiplier(scale):
    def multiply(x):
        return x * scale  # x 在 L 找到；scale 在 E 找到

    return multiply       # 返回函数本身，此时没有调用 multiply

double = make_multiplier(2.0)
print(double(3.0))  # 6.0
```

执行过程：

1. `make_multiplier(2.0)`：让外层参数 `scale` 绑定到 `2.0`。
2. 执行内部 `def`：创建 multiply 函数，暂不执行它的函数体。
3. `return multiply`：返回这个函数，并保留它访问外层 scale 的关联。
4. `double` 接住返回的函数，因此 double 是函数，不是数字。
5. `double(3.0)`：此时才执行 multiply，`x = 3.0`，计算 `3.0 * 2.0`。

这里 x 是每次调用 multiply 时传入的参数，scale 是创建该函数时引用的外层变量。

### 3. 加类型注解的同一个例子

```python
from collections.abc import Callable

def make_multiplier(scale: float) -> Callable[[float], float]:
    def multiply(x: float) -> float:
        return x * scale

    return multiply

double = make_multiplier(2.0)
print(double(3.0))  # 6.0
```

两版的计算逻辑相同。类型注解只是说明输入、输出的预期：

| 写法 | 含义 |
| --- | --- |
| `scale: float` | 外层函数接收一个浮点数 |
| `Callable[[float], float]` | 一个可调用对象，接收一个浮点数，返回一个浮点数 |
| `x: float`、`-> float` | 内部函数接收浮点数，返回浮点数 |

`Callable[[参数类型列表], 返回值类型]` 描述返回的函数，**不负责创建或调用函数**。

### 4. 不同外层调用，保留各自的变量绑定

同一套逻辑可以生成不同倍数的函数，每次调用外层函数都有各自的 scale 绑定：

```python
double = make_multiplier(2.0)
triple = make_multiplier(3.0)

print(double(5.0))  # 10.0
print(triple(5.0))  # 15.0
```

- `return multiply`：返回函数本身，以后再调用。
- `return multiply(3.0)`：立即调用，返回计算结果。
- `make_multiplier(2.0)` 给外层的 scale 传参；`double(3.0)` 给内部的 x 传参。

### 5. nonlocal：修改外层函数的变量绑定

闭包也可以保存不断变化的状态，例如计数器：

```python
def make_counter():
    count = 0

    def increment():
        nonlocal count  # 使用并修改外层 make_counter 中的 count
        count += 1
        return count

    return increment

counter = make_counter()  # 得到 increment，此时还没有加一
print(counter())  # 1
print(counter())  # 2
print(counter())  # 3，三次调用访问同一个外层 count
```

如果不写 nonlocal，因为 `count += 1` 包含赋值，Python 会把 count 视为 increment 的局部变量；但加一之前又要读取它，局部变量尚未赋值，因此报 `UnboundLocalError`。

| 操作 | 是否需要声明 |
| --- | --- |
| 只读取外层函数变量，如 `return count` | 不需要 nonlocal |
| 重新绑定外层函数变量，如 `count = 10`、`count += 1` | 需要 nonlocal |
| 修改外层列表内容，如 `items.append(1)` | 不需要 nonlocal，因为没有重新绑定 items |
| 重新绑定模块级变量 | 使用 global，而不是 nonlocal |

nonlocal 指向最近一层已有这个绑定的外层函数作用域，不能凭空创建一个外层变量。**判断关键是有没有给变量名重新赋值，不是有没有改变对象内容。**

### 6. 闭包保留绑定，不冻结值

```python
def outer():
    scale = 2

    def multiply(x):
        return x * scale

    scale = 3  # 改变同一个外层绑定
    return multiply

f = outer()
print(f(4))  # 12，读取的是变化后的 scale，而不是固定保存 2
```

装饰器常用同样的机制：包装函数 wrapper 通过闭包保留原函数 fn，之后再调用它。详见后面的「05｜装饰器」。

记住：**闭包保留对外层函数变量的访问；只读取不用声明，重新绑定用 nonlocal，原地修改对象不等于重新绑定。**

## 03｜类、数据模型与协议

日期：2026-10-23

### 1. 原例：让 Batch 支持求长度与遍历

```python
from dataclasses import dataclass
from collections.abc import Iterator

@dataclass
class Batch:
    samples: list[list[float]]  # 一批样本，每个样本是浮点数列表

    def __len__(self) -> int:
        return len(self.samples)  # 长度定义为样本数量

    def __iter__(self) -> Iterator[list[float]]:
        return iter(self.samples)  # 返回底层列表的迭代器

batch = Batch([[1.0, 2.0], [3.0, 4.0]])
print(len(batch))  # 2
for sample in batch:
    print(sample)  # 依次输出 [1.0, 2.0]、[3.0, 4.0]
```

- `Batch` 是类，`batch` 是实例，`batch.samples` 是实例的属性。
- `self` 表示当前实例，调用实例方法时由 Python 自动传入。
- `@dataclass` 根据字段自动生成 `__init__`、`__repr__`、`__eq__` 等方法；不会自动检查或转换字段类型。
- 初始化时的 `self.samples = samples`，表示把参数 samples 保存到当前对象的属性中。

**协议就是一组行为约定：实现对应方法，对象就能参与相应的 Python 操作。** 通常不要求继承特定父类。

### 2. 遍历时发生了什么？

`for sample in batch` 的过程：

1. `iter(batch)` 触发 `__iter__`，得到一个迭代器。
2. 不断从迭代器取出下一个元素。
3. 迭代器抛出 `StopIteration` 时，循环结束。

```python
it = iter(batch)
print(next(it))  # [1.0, 2.0]
print(next(it))  # [3.0, 4.0]
# next(it)      # 再取就会抛出 StopIteration
```

**可迭代对象提供迭代器；迭代器记录进度并提供下一个元素。** Batch 把取元素的工作交给列表迭代器，因此自身不必实现 `__next__`。

`Iterator[list[float]]` 表示：返回一个迭代器，每次取出的元素是 `list[float]`，即一个样本。

### 3. 常见特殊方法

| 方法 | 触发方式 | 用途 |
| --- | --- | --- |
| `__init__` | 创建实例的过程中 | 初始化实例状态 |
| `__repr__` | `repr(obj)`、调试显示 | 提供便于调试的对象表示 |
| `__call__` | `obj(...)` | 让实例像函数一样可调用 |
| `__enter__` / `__exit__` | `with` | 进入、退出上下文，常用于资源管理 |
| `__iter__` | `iter(obj)`、for 开始遍历 | 提供迭代器 |
| `__next__` | `next(iterator)` | 取得下一个元素，结束时抛出 StopIteration |
| `__getitem__` | `obj[key]` | 提供索引、切片或映射访问 |

### 4. 实例方法、类方法与静态方法

| 类型 | 装饰器 | 自动传入的第一个参数 | 常见用途 |
| --- | --- | --- | --- |
| 实例方法 | 无 | `self`：当前对象 | 操作具体对象的数据，如 Batch 的方法 |
| 类方法 | `@classmethod` | `cls`：当前类 | 备选构造器，如下面的 Device.parse |
| 静态方法 | `@staticmethod` | 无 | 在类中组织相关工具函数 |

`self` 和 `cls` 都是约定的名字，不是关键字。

### 5. 原例：从字符串创建 Device

```python
@dataclass
class Device:
    kind: str
    index: int

    @classmethod
    def parse(cls, value: str) -> "Device":
        kind, index = value.split(":")
        return cls(kind=kind, index=int(index))

device = Device.parse("cuda:0")
print(device.kind)   # cuda
print(device.index)  # 0
```

执行过程：

1. `Device.parse("cuda:0")`：Python 自动将 Device 类传给 cls，字符串传给 value。
2. `value.split(":")`：得到 `["cuda", "0"]`。
3. `kind, index = ...`：解包后 kind 为 `"cuda"`，index 为字符串 `"0"`。
4. `int(index)`：将 `"0"` 转成整数 `0`。
5. `cls(...)`：本次相当于 `Device(kind="cuda", index=0)`，创建并返回实例。

`kind=kind`：左边是构造时的参数名，右边是当前局部变量的值。

```python
a = Device(kind="cuda", index=0)  # 直接提供字段
b = Device.parse("cuda:0")       # 从字符串解析，再创建对象
```

这就是备选构造器：为创建对象提供另一种入口。用 `cls(...)`，可以根据实际调用的类创建实例，便于子类继承使用。

### 6. 返回类型为什么写成 "Device"？

**`-> "Device"` 是类型注解；`return cls(...)` 才真正创建并返回对象。** 引号不会让返回值变成字符串。这里返回的是 Device 实例，不是类本身。

类内部引用自身类型属于“前向引用”：方法定义时，外面的类可能还没有定义完成。

| 情况 | 是否需要引号 |
| --- | --- |
| Python 3.13 及以前，未启用延迟注解，在类内部引用自身类型 | 通常需要，否则可能报 NameError |
| 类型已经定义完成，例如在类外的函数注解中引用 Device | 可以直接写 `-> Device` |
| 文件开头使用 `from __future__ import annotations` | 本例可直接写 `-> Device` |
| Python 3.14 起默认延迟求值注解 | 本例通常可直接写 `-> Device` |

保留原例的 `-> "Device"` 即可，不必为了省略引号改写代码。版本差异参考：[Python 3.14 官方说明](https://docs.python.org/3.14/whatsnew/3.14.html#deferred-evaluation-of-annotations)。

记住：**特殊方法让对象支持标准操作；self 是实例，cls 是类，cls(...) 创建实例。**

## 04｜迭代器与生成器：按需生产数据

日期：2026-10-23

### 1. 三个概念与 yield

| 概念 | 含义 | 例子 |
| --- | --- | --- |
| 可迭代对象 | 能通过 `iter()` 提供迭代器 | 列表、文件对象 |
| 迭代器 | 保存遍历进度，通过 `next()` 逐个提供元素 | `iter([1, 2, 3])` |
| 生成器 | 用 yield 简洁实现的迭代器 | 调用下面的 read_batches 得到的对象 |

含有 `yield` 的普通函数是生成器函数。**调用时只创建生成器对象；下一次 next() 或 for 请求元素时，才执行函数体。**

- `return value`：返回结果并结束函数执行。
- `yield value`：交出一个值并暂停生成器，保留局部变量与执行位置；下次从 yield 之后继续。
- 执行完毕后，生成器通过 `StopIteration` 表示结束，for 会自动处理。

### 2. 原例：分批读取文件

```python
from collections.abc import Iterator

def read_batches(path: str, batch_size: int) -> Iterator[list[str]]:
    batch: list[str] = []
    with open(path, encoding="utf-8") as file:
        for line in file:
            batch.append(line.rstrip("\n"))  # 去掉行末换行符
            if len(batch) == batch_size:  # 当前批次已凑够指定数量
                yield batch  # 交出这一批，暂停生成器函数
                batch = []   # 下次恢复时，创建新列表，收集下一批
    if batch:  # 文件读完后，还有不足一批的剩余数据
        yield batch
```

`Iterator[list[str]]` 表示返回一个迭代器，每次取出的元素是一批数据，即字符串列表。这里使用正整数 batch_size。

假设 data.txt 有五行，内容依次为 A、B、C、D、E：

```python
g = read_batches("data.txt", 2)  # 只创建生成器，此时尚未打开文件

print(next(g))  # ['A', 'B']
print(next(g))  # ['C', 'D']
print(next(g))  # ['E']
# next(g)      # 再取会抛出 StopIteration
```

第一批的执行过程：读取 A、B → yield 交出列表并暂停 → 调用方处理这一批 → 下次请求时执行 `batch = []` → 继续读取 C、D。

通常使用 for，自动取下一批并在结束时停止：

```python
for batch in read_batches("data.txt", 2):
    print(batch)
```

### 3. 注释中容易混淆的地方

- **yield 暂停生成器函数，不会阻止调用方处理数据。** 下一次请求元素时，从 yield 后面的语句继续。
- **`batch = []` 不是清空旧列表，而是创建新列表并重新绑定。** 之前交给调用方的列表保持原样；若改成 `batch.clear()`，就会清空同一个旧列表，影响调用方拿到的数据。
- **`if batch` 判断列表是否非空，用于交出最后不足一批的数据。** 若行数刚好整除批次大小，batch 为空，就不会额外交出空列表。
- 循环里的 yield 暂停时，文件仍保持打开；正常读完并退出 with 后，文件关闭，再交出最后不足一批的数据。

### 4. 为什么节省内存？

逐行读取、按批交付，不需要一次性保存整个文件。**如果处理完不积累旧批次，内存主要与批次大小、每行长度及读取缓冲相关。**

```python
for batch in read_batches("data.txt", 100):
    print(batch)  # 实际项目中换成处理这一批的逻辑
```

如果收集全部结果，就会把所有批次重新放进内存：

```python
all_batches = list(read_batches("data.txt", 100))
```

还要记住：

- 同一个生成器耗尽后不能从头再来；重新调用 `read_batches(...)` 才会得到新生成器。
- 惰性执行也会推迟异常：文件不存在时，通常在首次 next() 或 for 开始迭代时才报错，而非创建生成器时。

记住：**需要一批才读取一批；yield 暂停，next 恢复；不积累全部结果，才能保留流式处理的内存优势。**

## 05｜装饰器：给函数调用增加行为

日期：2026-10-24；更新：2026-10-25

练习对应：[decorate.py](../../../projects/00-foundations/src/python/decorate.py)。

### 1. 普通装饰器：接收函数，返回包装函数

**装饰器接收原函数，返回包装函数；包装函数在调用原函数前后增加行为。** 下面用练习中的平方函数演示，计时改用适合测量间隔的 perf_counter：

```python
from time import perf_counter

def decorator(func):
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)  # 调用原函数，取得结果
        elapsed = perf_counter() - start
        print(f"{func.__name__} execution time: {elapsed:.6f} seconds.")
        print(result)  # 显示结果
        return result  # 把结果交给 wrapper 的调用方

    return wrapper  # 交出函数本身，此时不执行 wrapper

@decorator
def square(x):
    return x * x

value = square(10)  # 输出耗时和 100，同时 value 得到 100
```

`@decorator` 是装饰器语法，不是类型注解，等价于在函数定义完成后执行：

```python
square = decorator(square)
```

也可以拆成 `original = square` → `wrapped = decorator(original)` → `square = wrapped`。wrapper 通过闭包保留 func 对原函数的引用，外部 square 改名绑定不会改变 func，因此不会递归调用自身。

| 阶段 | 操作 | 结果 |
| --- | --- | --- |
| 装饰时 | decorator 接收原 square，返回 wrapper | square 改为指向 wrapper，尚未执行平方计算 |
| 调用时 | `square(10)` 进入 wrapper，再调用 func | 输出耗时，返回原函数的结果 100 |

### 2. 为什么要 return？返回给谁？

| 写法 | 含义 |
| --- | --- |
| `def wrapper():` | 定义函数；这里的括号是定义语法 |
| `wrapper` | 函数对象本身 |
| `wrapper()` | 调用函数，得到执行结果 |
| decorator 中的 `return wrapper` | 把包装函数交给 decorator 的调用方，用来替换原函数 |
| wrapper 中的 `return result` | 把原函数的计算结果交给 wrapper 的调用方 |
| `return func(...)` | 先调用 func，再把它的结果返回给当前函数的调用方 |

**打印不等于返回。** 删除 wrapper 中的 `return result` 后，虽然仍能打印 100，但 `value = square(10)` 得到的是 None，`square(10) + 5` 也无法正常计算。

- wrapper 是习惯命名，可以改为 inner 等名字，但 `return wrapper` 也要同步改名。
- 外层 decorator 如果改名为 abc，就对应使用 `@abc`；只改内部 wrapper 的名字，不改变外面的装饰器名字。
- `@` 后面的装饰器需要事先可用；本例中它接收原函数，并返回一个可以继续调用的包装函数。

### 3. *args 和 **kwargs：收集与展开参数

**这里的星号不是指针。定义函数时收集参数，调用函数时展开参数。**

```python
def show(*args, **kwargs):
    print(args)    # 位置参数收集为元组
    print(kwargs)  # 关键字参数收集为字典

show(10, 20, name="小明")
# (10, 20)
# {'name': '小明'}
```

args、kwargs 是约定的变量名，起作用的是星号。包装函数常用下面的方式，把参数转交给原函数：

```python
def wrapper(*args, **kwargs):
    return fn(*args, **kwargs)
```

例如调用 `wrapper(2, b=3)`：先收集成 `args = (2,)`、`kwargs = {"b": 3}`，再展开成 `fn(2, b=3)`。wrapper 能收集多种参数形式，但原函数仍须能接受这些参数；square 只有一个参数 x，传两个位置参数依然会报错。

### 4. 装饰器工厂：先接收配置，再接收函数

```python
import time
from functools import wraps

def timer(threshold):  # 第一层：接收阈值，单位为秒
    def decorator(func):  # 第二层：接收原函数
        @wraps(func)
        def wrapper(*args, **kwargs):  # 第三层：处理实际调用
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            if elapsed > threshold:
                print(f"{func.__name__} execution time: {elapsed:.6f} seconds.")
            return result
        return wrapper
    return decorator

@timer(0.2)
def sleep_04():
    time.sleep(0.4)

sleep_04()  # 等待约 0.4 秒，超过 0.2 秒，因此输出耗时
print(sleep_04.__name__)  # sleep_04，wraps 保留原函数名
```

`@timer(0.2)` 等价于 `sleep_04 = timer(0.2)(sleep_04)`，逐步展开为：

```python
def sleep_04():  # 先定义未装饰的原函数
    time.sleep(0.4)

original = sleep_04
configured_decorator = timer(0.2)
wrapped = configured_decorator(original)
sleep_04 = wrapped
# 上面只是包装；之后 sleep_04() 才执行原函数
```

| 层次 | 调用时机 | 返回内容 |
| --- | --- | --- |
| `timer(threshold)` | 执行 `timer(0.2)` 时 | 配置好的 decorator |
| `decorator(func)` | 将原函数交给上述 decorator 时 | wrapper 函数 |
| `wrapper(*args, **kwargs)` | 之后调用被装饰函数时 | 原函数的执行结果 |

**三层 return 返回不同东西：装饰器、包装函数、计算结果。** 前两层没返回对应函数，后续调用就无法按预期进行；第三层没返回结果，调用方就只能得到 None。

- wrapper 通过闭包保留 func 和 threshold；timer 返回的 decorator 也保留了阈值所需的外层绑定。
- sleep_04 原函数没有 return，所以它的结果是 None，wrapper 将这个 None 原样返回。
- timer 叫**装饰器工厂**，不是生成器函数；这里没有 yield。普通 `@decorator` 直接接收函数，`@timer(0.2)` 则先接收配置、产生装饰器。

### 5. 保留类型信息的计时装饰器

```python
from collections.abc import Callable
from functools import wraps
from time import perf_counter
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def timed(fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = perf_counter()  # 每次调用时记录开始时间
        try:
            return fn(*args, **kwargs)  # 转交参数并返回原函数结果
        finally:
            elapsed_ms = (perf_counter() - start) * 1_000
            print(f"{fn.__name__}: {elapsed_ms:.3f} ms")
    return wrapper

@timed
def preprocess(values: list[float]) -> list[float]:
    return [value * 2 for value in values]

result = preprocess([1.0, 2.0])  # 调用时打印耗时
print(result)  # [2.0, 4.0]
```

`@timed` 等价于 `preprocess = timed(preprocess)`。调用顺序：进入 wrapper → 记录时间 → 执行原函数 → finally 打印耗时 → 将结果返回给调用方。

| 名字或写法 | 含义 |
| --- | --- |
| `Callable` | 描述可调用对象的类型；如 `Callable[[int, int], int]` 表示接收两个整数、返回整数的函数等对象 |
| `P = ParamSpec("P")` | 用 P 代表原函数的一整套参数规格 |
| `R = TypeVar("R")` | 用 R 代表原函数的返回值类型 |
| `Callable[P, R]` | 接收 P 对应的参数、返回 R 类型结果的可调用对象 |
| `*args: P.args` | 收集位置参数，注解说明它们对应原函数的位置参数部分 |
| `**kwargs: P.kwargs` | 收集关键字参数，注解说明它们对应原函数的关键字参数部分 |

可以先去掉注解，按 `def wrapper(*args, **kwargs):` 理解。**参数转发靠星号语法；P、R 帮助编辑器和类型检查工具保留原函数的参数与返回类型信息，不会自动转换数据。**

### 6. wraps、finally 和计时细节

- `@wraps(fn)`：让包装函数保留原函数的名字、文档字符串等元信息，并用 `__wrapped__` 指向原函数。没有它，装饰后的 `preprocess.__name__` 通常是 `"wrapper"`；有它则是 `"preprocess"`。
- wraps 不负责执行原函数，真正调用仍靠 `fn(*args, **kwargs)`。代码中的 fn 本来就指向原函数，因此 `fn.__name__` 本身不依赖 wraps。
- `try` 中执行 return 时，先算出结果，再执行 finally，最后返回结果。原函数报错时，也先执行 finally，再继续传播异常；这里没有捕获异常。
- 前面的普通装饰器和阈值装饰器在原函数报错时不会执行后面的计时输出；若需要失败时也记录耗时，可采用上面 try/finally 的结构。
- `perf_counter()` 用于测量时间间隔，差值单位为秒；乘 `1_000` 转为毫秒。`1_000` 就是 1000，`:.3f` 表示保留三位小数。
- `[value * 2 for value in values]` 是列表推导式：把每个元素乘 2，组成新列表。

装饰器常用于日志、缓存、权限检查和计时。如果只有一个调用点需要计时，直接在调用前后记录时间也很清楚。

记住：**普通装饰器接函数，装饰器工厂先接配置；装饰时返回函数，调用时返回结果，wraps 保留元信息。**

## 06｜上下文管理器：明确进入与退出的边界

日期：2026-10-24

### 1. with 与 contextmanager

**上下文管理器统一安排进入时的准备和退出时的收尾。** 例如文件在退出 with 时关闭，即使代码块中发生异常，也执行关闭操作：

```python
with open("data.txt", encoding="utf-8") as file:
    text = file.read()
# 离开 with 后，文件已经关闭
```

`@contextmanager` 把符合要求的生成器函数转换成上下文管理器，让它可以用于 with。正常的一次使用要求生成器恰好执行一次 yield：yield 前准备，暂停时执行 with 内的代码，恢复后收尾。

### 2. 原例：给一个代码块计时

```python
from contextlib import contextmanager
from collections.abc import Iterator
from time import perf_counter

@contextmanager
def timer(name: str) -> Iterator[None]:
    start = perf_counter()  # 进入 with：记录开始时间
    try:
        yield  # 暂停生成器，让 with 内的代码执行
    finally:
        # 离开 with：无论正常结束还是抛出异常，都执行收尾
        elapsed_ms = (perf_counter() - start) * 1_000
        print(f"{name}: {elapsed_ms:.3f} ms")

with timer("load data"):
    data = [value for value in range(100_000)]
```

执行顺序：

1. `timer("load data")` 创建上下文管理器。
2. 进入 with，执行底层生成器，记录 start。
3. 到达 yield，生成器暂停。
4. 执行 with 内的代码，创建包含 0～99_999 的列表。
5. 离开 with，恢复生成器，执行 finally，打印耗时。

输出类似 `load data: 2.350 ms`，实际数值每次不同。时间差单位为秒，乘 1000 转毫秒；`:.3f` 表示保留三位小数。

**yield 没有把代码块接收进函数；执行顺序由 with 和上下文管理器协调。** 此例收尾是打印耗时，并没有关闭文件等资源操作。

### 3. 为什么发生异常也能收尾？

```python
with timer("load data"):
    raise ValueError("读取失败")
```

异常会经上下文管理器传回生成器暂停的 yield 处。因为 yield 位于 try/finally 内，所以先执行 finally 打印耗时，再向外传播 ValueError。

**执行收尾不等于消除异常。** 本例没有 except，不会捕获并消除代码块中的异常。

### 4. Iterator[None] 与 as

`Iterator[None]` 描述底层生成器：裸写 `yield` 等价于 `yield None`。经过 `@contextmanager` 装饰后，调用 timer 得到的是上下文管理器。

`with ... as value` 中的 value 接收 yield 交出的值：

```python
with timer("load data") as value:
    print(value)  # None，因为 timer 中 yield 没有指定值
```

### 5. 与特殊方法、作用域和 RAII 的关系

| 方法 | 触发时机 | 本例中的作用 |
| --- | --- | --- |
| `__enter__` | 进入 with | 推进生成器到 yield，完成准备 |
| `__exit__` | 离开 with，包括异常退出 | 恢复生成器或传入异常，执行收尾 |

`@contextmanager` 帮我们实现协调逻辑，因此不用自己编写这两个方法。

- **with 不创建新的变量作用域。** 原例结束后仍可访问 data；它划定的是上下文的使用边界。
- 上下文管理也可以用于锁、临时目录和运行状态的设置与恢复；例如自动混合精度上下文会在退出时恢复相应状态。
- 与 C++ RAII 的共同目标是给资源或状态的生命周期设置清晰的收尾边界；Python 这里通过 with 的进入、退出协议实现。

记住：**进入时准备，yield 处暂停，代码块结束后收尾；finally 让异常路径也执行清理逻辑。**

## 07｜异常处理：只捕获能够处理的错误

日期：2026-10-24

### 1. 原例：解析正整数配置

```python
def parse_world_size(raw: str) -> int:
    try:
        world_size = int(raw)  # 尝试把字符串转换成整数
    except ValueError as exc:  # 捕获转换失败，exc 是原异常对象
        raise ValueError(f"WORLD_SIZE 必须是整数，实际为 {raw!r}") from exc

    if world_size <= 0:
        raise ValueError("WORLD_SIZE 必须大于 0")
    return world_size
```

- `"4"` → 返回 4；`"abc"` → 转换失败；`"0"` → 转换成功，但不符合正数要求。
- `raise ... from exc`：抛出带有配置上下文的新异常，同时保留原始原因链。
- `{raw!r}`：使用 repr 展示值，例如字符串 abc 显示为 `'abc'`。
- try 只包住转换操作，避免把其他地方的错误误报成“转换失败”。

### 2. 与 Java 的区别

**核心机制相近：except 对应 catch，raise 对应 throw，finally 用于收尾。**

| Python | Java 中的对应或区别 |
| --- | --- |
| `except ValueError as exc:` | 类似 `catch (NumberFormatException exc)`，异常类型按具体操作选择 |
| `raise ValueError("说明")` | 类似 `throw new IllegalArgumentException("说明")` |
| `raise NewError("说明") from exc` | 类似 `throw new NewException("说明", exc)`，保留 cause |
| `finally:` | 类似 Java finally，正常返回或异常退出时执行收尾 |
| `else:` | Java 无直接对应语法；try 正常执行结束时执行，else 内异常不由前面的 except 捕获 |
| 无受检异常机制 | Java 某些异常必须捕获或通过 throws 声明；Python 无此编译期要求 |

### 3. 捕获原则

- 捕获具体异常。裸 `except:` 连 KeyboardInterrupt 等也会捕获；`except: pass` 容易让程序带着错误继续运行。
- 能恢复、补充上下文或转换异常层级时才捕获；否则让异常向外传播。
- `raise` 单独使用可在 except 中原样重新抛出当前异常；创建新异常时用 `raise ... from exc` 明确保留根因。
- 不把异常作为正常的高频控制流，尤其在性能敏感循环中。

记住：**捕获要具体，处理要有意义；重新包装异常时保留根因。**

## 08｜类型标注与数据类

日期：2026-10-24

### 1. 原例：保存配置并分配数据

```python
from dataclasses import dataclass
from collections.abc import Sequence

@dataclass(frozen=True)
class ShardSpec:
    rank: int        # 当前进程编号，从 0 开始
    world_size: int  # 进程总数

def shard(values: Sequence[int], spec: ShardSpec) -> Sequence[int]:
    return values[spec.rank::spec.world_size]
```

- `@dataclass`：根据字段生成初始化、打印表示、按字段比较等常用方法，适合主要承载数据的对象。
- `frozen=True`：创建后不能通过普通赋值修改或删除字段，如 `spec.rank = 2` 会报错；不会递归冻结字段内的列表等可变对象。
- **类型标注不自动校验或转换数据。** `ShardSpec(rank="abc", world_size=3)` 本身仍能创建；frozen 也不负责验证字段类型。

### 2. 切片怎样完成分片？

`values[rank::world_size]` 使用 `序列[开始:结束:步长]`，省略结束位置：从 rank 开始，每隔 world_size 个位置取一个。

```python
values = list(range(10))  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

print(shard(values, ShardSpec(0, 3)))  # [0, 3, 6, 9]
print(shard(values, ShardSpec(1, 3)))  # [1, 4, 7]
print(shard(values, ShardSpec(2, 3)))  # [2, 5, 8]
```

这是交错分片，几个进程轮流领取数据。正确配置要求 `world_size > 0`、`0 <= rank < world_size`；原例未主动校验这些条件，类型标注 int 也不表达正数约束。

### 3. Iterable、Sequence 与具体容器怎么选？

| 标注 | 要求或含义 | 例子 |
| --- | --- | --- |
| `Iterable[int]` | 能逐个遍历整数 | 列表、元组、集合、生成器 |
| `Sequence[int]` | 整数序列，支持按位置访问、切片、求长度等 | 列表、元组、range |
| `list[int]` | 具体的整数列表 | list |
| `dict[str, int]` | 键为字符串、值为整数的字典 | dict |
| `T | None` | 某种类型或 None，T 泛指一个类型 | `name: str | None = None` |

**根据实际需要的能力标注参数。** 仅遍历可用 Iterable；原例要切片，所以用 Sequence，不能只要求 Iterable。

返回值也写 Sequence，是因为切片结果不一定是列表：列表切片返回列表，元组切片返回元组。如果承诺一定返回列表，可改成 `-> list[int]`，并返回 `list(values[spec.rank::spec.world_size])`。

### 4. Protocol：通过结构描述接口

```python
from typing import Protocol

class Runnable(Protocol):
    def run(self) -> None:
        ...  # 只声明接口，不提供实现

def execute(task: Runnable) -> None:
    task.run()

class Job:
    def run(self) -> None:
        print("执行任务")

execute(Job())  # Job 无需显式继承 Runnable
```

Protocol 让类型检查工具根据对象是否提供兼容的方法判断接口是否匹配，减少不必要的继承；它不自动验证运行时传入的对象。

记住：**类型标注说明接口，数据类组织数据，frozen 限制字段修改；业务约束仍需代码检查。** 公共接口优先标清，显而易见的局部变量不必逐个标注。

## 09｜类与对象补充：属性、初始化与方法

日期：2026-10-25

### 1. 类属性与实例属性

```python
class StudyRecord:
    category = "学习记录"  # 类属性，保存在类上

    subject: str  # 可选：提前标注实例属性类型，不创建属性
    minutes: int

    def __init__(self, subject):
        self.subject = subject  # 创建并初始化当前对象的实例属性
        self.minutes = 0

    def add(self, minutes):
        self.minutes = self.minutes + minutes  # 更新当前对象的属性

    @classmethod
    def get_category(cls):
        return cls.category

python_record = StudyRecord("Python")
reading_record = StudyRecord("读书")
python_record.add(15)

print(python_record.minutes)        # 15
print(reading_record.minutes)       # 0
print(StudyRecord.get_category())   # 学习记录
```

| 写法 | 含义 |
| --- | --- |
| 类体中的 `category = "学习记录"` | 创建类属性，可通过 `StudyRecord.category` 访问 |
| `self.subject = subject` | 创建或更新当前实例的属性，各实例保存自己的值 |
| 类体中的 `subject: str` | 仅标注预期类型，不创建实际属性，也不自动校验类型 |

**普通类的实例属性不必提前声明，通常在 __init__ 中统一初始化。** 也可以在其他实例方法中通过 self 赋值新增，或在对象外写 `python_record.note = "学习类"`。某些类会限制动态添加属性。

实例没有同名实例属性时，也能查找到类属性，如 `python_record.category`。dataclass 会专门处理字段注解，自动生成初始化代码，不能把它与普通类的单纯注解混为一谈。

### 2. Python 的“构造函数”

创建 `StudyRecord("Python")` 时，先创建实例，再自动调用 __init__ 初始化它；self 自动对应新实例，subject 接收 `"Python"`。

| 方法 | 职责 |
| --- | --- |
| `__new__` | 创建并返回实例，普通业务类通常不用重写 |
| `__init__` | 初始化已有实例，日常所说的“构造函数”通常指它 |

- __init__ 是实例方法，不加 @classmethod；它应返回 None，通常不写 return。
- 不需要自定义初始化逻辑时，可以不写 __init__。
- `self.subject = subject` 左边是对象属性，右边是传入的参数。

### 3. 写在类里的函数，不一定是“类方法”

| 类型 | 定义方式 | 自动传入 | 用途 |
| --- | --- | --- | --- |
| 实例方法 | `def show(self):` | 当前实例 | 操作具体对象的状态 |
| 类方法 | `@classmethod` 配合 `def show(cls):` | 当前类 | 使用当前类，如读取类配置或创建实例 |
| 静态方法 | `@staticmethod` 配合 `def show():` | 无 | 组织不需要实例或类的工具函数 |

如果在普通类中直接写：

```python
class ClassA:
    def fun1():
        print("我是 fun1")

ClassA.fun1()    # 可以执行
# ClassA().fun1()  # TypeError：实例调用会自动传入对象，但函数未接收参数
```

**没有 self，不会自动变成静态方法或类方法。** 若希望实例调用，应接收实例参数；若希望不自动接收对象，可使用 @staticmethod。

### 4. classmethod 和 cls 的易混点

- @classmethod 是装饰器，负责调用时自动传入类；第一个参数负责接住它，习惯命名为 cls，也可以改成 klass 等名字。
- 类方法即使不读取类属性，也需要接收类参数。例如 `@classmethod` 下的 `def create(cls): return cls()`，通过当前类创建实例。
- **访问类属性不要求使用类方法。** 实例方法可通过 `self.category` 查找，其他代码也可通过 `StudyRecord.category` 访问。
- 是否定义类方法取决于是否需要“当前类”，不应给所有定义在类里的方法都加 @classmethod。

记住：**类属性通常在类体赋值，实例属性通常在初始化时赋值；类型注解不创建属性，self 接实例，cls 接类。**

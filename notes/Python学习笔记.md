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

日期：2026-10-23

### 1. LEGB：名字去哪里找？

普通函数中读取名字时，按下面的顺序查找，找到就停止；都找不到则报 `NameError`。

| 顺序 | 作用域 | 含义 |
| --- | --- | --- |
| L：Local | 局部 | 当前函数的参数、局部变量 |
| E：Enclosing | 外层函数 | 在代码定义上包住当前函数的外层函数作用域 |
| G：Global | 模块 | 当前模块（通常是所在的 `.py` 文件）的顶层名字 |
| B：Builtins | 内置 | Python 提供的名字，如 `len`、`print` |

注意：**外层作用域看函数定义时的嵌套关系，不看是谁调用它。**

### 2. 不加类型注解的例子

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

**闭包：函数及其引用的外层变量绑定。外层函数调用结束后，返回的函数仍可访问这些绑定。** 这不是把所有外层变量的值都复制、冻结一份。

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

### 4. 用途与易混点

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

记住：**先给 scale，得到函数；再给 x，得到结果。闭包让函数继续访问外层变量。**

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

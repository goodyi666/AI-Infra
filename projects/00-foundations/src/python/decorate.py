import time
import functools

def square(x):
    return x*x

def decorator(func): #传入一个函数，并用装饰器来装饰它
    def warpper(*args,**kwargs): #收集参数：由于是装饰传来的函数，所以要和传入函数的参数列表一致，但由于不知道参数列表，可以用*args,**kwargs来传入任意参数
         start_time = time.time()
         result = func(*args,**kwargs) #展开参数
         end_time = time.time()
         print(f'{func.__name__} execution time: {end_time-start_time} seconds.')
         print(result)
         return result  # 把result 返回给 warpper ,这里为什么要返回？
    return warpper  # 返回装饰后的函数，这里算是闭包吗？

square=decorator(square)
square(10)

@decorator #更简单的方法使用装饰器，语法糖
def square2(x):
    return x*x

#也就是说，@decorator 就相当于 square2 = decorator(square2)
square2(10)

#装饰器的生成器
def timer(threshold):
    def decorator(func):
        @functools.wraps(func) # 保留原函数的元信息
        def warpper(*args,**kwargs):
            start_time = time.time()
            result = func(*args,**kwargs)
            end_time = time.time()
            execution_time = end_time-start_time
            if execution_time > threshold:
                print(f'{func.__name__} execution time: {execution_time} seconds.')
            return result
        return warpper #返回warpper函数
    return decorator # 返回装饰器 为啥都要返回？

@timer(0.2)
def sleep_04():
    time.sleep(0.4)

sleep_04()

print(sleep_04.__name__) # 输出 sleep_04
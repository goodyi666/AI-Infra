f = open('test.txt')
try:
    data = f.read()
finally:
    f.close()

print(data)

with open('test.txt') as f:
    data = f.read()

print(data)

# 定义一个上下文管理器类:需要写__enter__和__exit__方法
class MyOpen:
    def __init__(self,filepath):
        print('Entering construtor of MyOpen')
        self.filepath = filepath

    def __enter__(self):
        print('Entering __enter__ method of MyOpen')
        return self.filepath

    def __exit__(self, exc_type, exc_val, traceback):
        print('Entering __exit__ method of MyOpen')

with MyOpen('test.txt') as f:
    print(f)
        
class A:
    _instance = None
    _init = False
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self):
        if A._init:
            return
        print('A')
        A._init = True
        


class B(A):
    def __init__(self):
        super().__init__()
        
        
        

class C(A):
    def __init__(self):
        super().__init__()
       
       
class D:
    def __init__(self):
        print('dsdsds')
        a = A()
        
b = B()

c=C()

d= D()
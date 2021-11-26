import sys

def test_function(n):
    return n

def repeat(n):
    def dec(genuine_function):
        def fake_function(arg):
            result = arg
            for i in range(n):
                result = genuine_function(result)
            return result
        return fake_function
    return dec

@repeat(2)
def plus_1(x):
    return x + 1

@repeat(0)
def mul_2(x):
    return x * 2

print(plus_1(3))
print(mul_2(4))
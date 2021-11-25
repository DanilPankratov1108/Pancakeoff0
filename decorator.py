import sys

def test_function(n):
    return n

def repeat(n):
    def dec(genuine_function):
        def fake_function(*args, **kwargs):
            result = genuine_function(*args, **kwargs)
            return result
        return fake_function
    return dec

@repeat(2)
def plus_1(y, x):
    return y + x + 1

@repeat(0)
def mul_2(y, x):
    return y + x * 2

print(plus_1(2,2))
print(mul_2(0,2))
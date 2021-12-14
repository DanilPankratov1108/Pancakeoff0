
import math

print("Простое ли число ?")

a = int(input())

def test(a):
    if (math.factorial(a-1) + 1) % a == 0:
        return True
    else:
        return False

b = test(a)
print(b)

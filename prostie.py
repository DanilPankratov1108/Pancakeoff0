
import math

a = int(input())

def test(a):
    if (math.factorial(a-1) + 1) % a!=0:
        print("Число составное")
    else:
        print("Число простое")

b = test(a)
print(b)

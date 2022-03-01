
import math

def test(a):
    if (math.factorial(a-1) + 1) % a == 0:
        return True
    else:
        return False

print("Простое ли число ?")

a = int(input())
if __name__ == "__main__":
 b1 = test(a)
 print(b1)

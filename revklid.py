
a = int(input())
b = int(input())

def egcd(a, b):
    if b == 0:
        return a, 1, 0
    else:
        d, x, y = egcd(b, a % b)
        return d, y, x - y * (a // b)

p = egcd(a, b)

print(p)


a = int(input())
b = int(input())

def gcd(a,b):
    while b != 0: 
        a, b = b, a % b 
    return a
    
d = int(gcd(a,b))

print(d)

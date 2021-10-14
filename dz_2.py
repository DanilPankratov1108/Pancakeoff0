import math
import numpy as nm
import matplotlib.pyplot as mp
ITERATIONS = 20


def my_cos(x):
    fact = 1

    pow = 1
    sum = 0
    for n in range(0, ITERATIONS, 2):
        sum += (((-1)**(n/2)) *pow) / fact
        pow *=x*x

        fact =fact *(n+1)*(n+2)
    return sum




print(math.cos(0.4))
print(my_cos(0.4))
p = nm.pi
k=2
x=nm.linspace(-p*k,p*k,100)
mp.plot(x,my_cos(x),)
mp.plot(x,nm.cos(x),'--',color = 'red')
mp.show()

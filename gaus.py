
import numpy as np
from numpy import array
from numpy.linalg import norm
from numpy.linalg import solve as solve_out_of_the_box

def gauss(a, b):
    a = a.copy()
    b = b.copy()
    
    for j in range(0, 3):
        for i in range(j + 1, 4):
            c = a[i][j] / a[j][j]
            a[i] -= a[j] * c
            b[i] -= b[j] * c
        for i in range(4):
            d = a[i][i]
            a[i] /= d
            b[i] /= d

    for j in range(2, -1, -1):
        for i in range(3, j, -1):
            c = a[j][i]
            a[j] -= a[i] * c
            b[j] -= b[i] * c

    print(a,b)
    return b

a = array([
    [1.5, 2.0, 1.5, 2.0],
    [3.0, 2.0, 4.0, 1.0],
    [1.0, 6.0, 0.0, 4.0],
    [2.0, 1.0, 4.0, 3.0]
], dtype=float)

b = array([5, 6, 7, 8], dtype=float)

x = gauss(a,b)
print(a*x)

oob_solution = solve_out_of_the_box(a, b)
solution = gauss(a, b)

print(solution)
print("Макс отклонение компоненты решения:", norm(solution-oob_solution, ord=1))


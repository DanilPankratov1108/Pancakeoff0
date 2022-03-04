import numpy as np


def gauss(a, b):
    a = a.copy()
    b = b.copy()
    N = len(a)

    for j in range(0, N):
        for i in range(j + 1, N):
            if a[j][j] != 0:
                c = a[i][j] / a[j][j]
                a[i] -= a[j] * c
                b[i] -= b[j] * c
        for i in range(N):
            d = a[i][i]
            a[i] /= d
            b[i] /= d

    for j in range(N-2, -1, -1):
        for i in range(N-1, j, -1):
            c = a[j][i]
            a[j] -= a[i] * c
            b[j] -= b[i] * c

    print( b)
    return b

from gaus import gauss
import random as rand
import numpy as np
from numpy.linalg import norm
from numpy.linalg import solve as solve_out_of_the_box


N = rand.randint(1 , 100)


a = np.array([[float(rand.randint(-20, 20))
             for i in range(N)]for j in range(N)])

b = np.array([float(rand.randint(-20, 20)) for i in range(N)])

gauss(a, b)

oob_solution = solve_out_of_the_box(a, b)
solution = gauss(a, b)

print(solution)
print("Макс отклонение компоненты решения:",
      norm(solution-oob_solution, ord=1))
print(N)
import numpy as np
from matplotlib import pyplot as pp

MODEL_G = 9.81
MODEL_DT = 0.001

class Body:
    def __init__(self, x, y, vx, vy):

        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

        self.trajectory_x = []
        self.trajectory_y = []

    def advance(self):
       
        self.trajectory_x.append(self.x)
        self.trajectory_y.append(self.y)


        self.x += self.vx * MODEL_DT
        self.y += self.vy * MODEL_DT
        self.vy -= MODEL_G * MODEL_DT


class Rocket(Body):

    def __init__(self, x, y, mr, mo, ux, uy, dm):
        
        super().__init__(x, y, 10, 100)

        self.x = x
        self.y = y
        self.mr = mr
        self.mo = mo
        self.ux = ux
        self.uy = uy
        self.dm = dm
        self.M = mr + mo


    def advance(self):
        super().advance()
        self.mo += self.dm * MODEL_DT
        self.M += self.dm * MODEL_DT
        self.vx +=- (self.ux * self.dm) / self.M * MODEL_DT
        self.vy +=- (self.uy * self.dm) / self.M * MODEL_DT
        
            
b = Body(0, 0, 10, 100)
r = Rocket(0, 0, 1, 15, 1, 2, -3) 

bodies = [b, r]

for t in np.arange(0, 20, MODEL_DT):
    for b in bodies:
        b.advance()

for b in bodies:
    pp.plot(b.trajectory_x, b.trajectory_y)
pp.show()
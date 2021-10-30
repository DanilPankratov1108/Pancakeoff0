import math
from matplotlib import pyplot as pp
import numpy as np

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
    def __init__(self, x, y, mass_rock, mass_oil, ux, uy, dm,):

        super().__init__(x, y, 10, 100)

        self.mass_rock = mass_rock
        self.mass_oil = mass_oil
        self.ux = ux
        self.uy = uy
        self.dm = dm
        self.M = mass_rock + mass_oil

    def advance(self):
        super().advance()
        if self.mass_oil > 0:
            self.M += self.dm * MODEL_DT
            self.mass_oil += self.dm * MODEL_DT
            if MODEL_DT * MODEL_G <= -((self.uy * self.dm) / (self.M)) * MODEL_DT:
                self.vx += -((self.ux * self.dm) / (self.M)) * MODEL_DT
                self.vy += -((self.uy * self.dm) / (self.M)) * MODEL_DT
            else:
                self.vy += MODEL_DT * MODEL_G 
           
b = Body(0, 0, 10, 100)
r = Rocket(0, 0, 1, 15, 1, 1, -2.5)

bodies = [b, r]

for t in np.arange(0, 20, MODEL_DT):
    for b in bodies:
        b.advance()

for b in bodies:
    pp.plot(b.trajectory_x, b.trajectory_y)
pp.show()
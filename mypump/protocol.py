from runze3 import mypump, ser
import time
from interruptingcow import timeout

mp = mypump()

timer = 10

timeout = time.time()+timer

"""Рецепт"""

#mp.init()

while True:
        mp.set_volume(60, 640, 1)
        mp.output_volume(60, 640, 1)
        if time.time() > timeout:
            break














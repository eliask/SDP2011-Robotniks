from robot_interface2 import RealRobotInterface
import time
from math import *

IF = RealRobotInterface()

DT = 0.45
for t in range(1/DT):
    IF.sendMessage()
    time.sleep(DT)

print "Starting..."

for i in range(50):
    print i
    IF.steer_left(radians(30*i % 360))
    IF.steer_right(radians(30*i % 360))
    IF.sendMessage()
    time.sleep(DT)
IF.sendMessage()
time.sleep(1)

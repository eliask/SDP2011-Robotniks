from robot_interface2 import RealRobotInterface
import time
from math import *

IF = RealRobotInterface()

DT = 0.8
for t in range(3/DT):
    IF.sendMessage()
    time.sleep(DT)

print "Starting..."

for i in range(30):
    IF.steer_left(radians(120*i % 360))
    IF.steer_right(radians(120*i % 360))
    print "At %d degrees" % (120*i % 360)
    IF.sendMessage()
    time.sleep(DT)
IF.sendMessage()
time.sleep(1)

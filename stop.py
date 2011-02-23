#! /usr/bin/env python

from communication.robot_interface2 import *
interface = RealRobotInterface(False)
interface.reset()
interface.sendMessage()
print "Done."

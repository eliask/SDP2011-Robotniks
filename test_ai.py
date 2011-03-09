#! /usr/bin/env python
# -*- coding: utf-8 -*-

from vision2.vision import *
from common.world import *
from strategy.strategies import *
from communication.robot_interface2 import *
import sys

import logging
#logging.basicConfig(level=logging.DEBUG)

args = len(sys.argv)
if args < 3:
    print "Usage: vision.py <colour> [ai]"
    sys.exit(2)

colour = sys.argv[1]
world = World()
v = Vision(world, sys.argv[3:])
ai_name = sys.argv[2]

ai = strategies[ai_name]( world, RealRobotInterface() )
ai.setColour(colour)

while True:
    v.processFrame()
    ai.run()
    ai.sendMessage()

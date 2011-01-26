#! /usr/bin/env python
# -*- coding: utf-8 -*-

from vision.vision import *
from common.world import *
from strategy.strategies import *
from communication.client import *
import sys

args = len(sys.argv)
if args == 2:
    _, colour = sys.argv
    world = World(colour)
    v = Vision(world)
elif args == 3:
    _, colour, filename = sys.argv
    world = World(colour)
    v = Vision(world, filename)
else:
    print "Usage: vision.py <colour> [filename]"
    sys.exit(2)

ai = strategies['main']( world, RealRobotInterface() )
while True:
    v.processFrame()
    ai.run()

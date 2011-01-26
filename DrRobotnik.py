#! /usr/bin/env python
# -*- coding: utf-8 -*-

from vision.vision import *
from common.world import *
from strategy.strategies import *
from communication.client import *
import sys

args = len(sys.argv)
colour = sys.argv[1]

ai_name = 'main'
world = World(colour)
v = Vision(world)
if args > 2:
    ai_name = sys.argv[2]
elif args < 2:
    print "Usage: vision.py <colour> [ai name]"
    sys.exit(2)

ai = strategies[ai_name]( world, RealRobotInterface() )
while True:
    v.processFrame()
    ai.run()

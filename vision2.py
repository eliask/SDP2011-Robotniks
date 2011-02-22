#! /usr/bin/env python
# -*- coding: utf-8 -*-

from vision2.vision import Vision
from common.world import World
import sys

import logging
#logging.basicConfig(level=logging.DEBUG)

args = len(sys.argv)
if args < 2:
    print "Usage: vision.py <colour> [filename]"
    sys.exit(2)

colour = sys.argv[1]
world = World(colour)
if args == 2:
    v = Vision(world)
elif args > 2:
    files = sys.argv[2:]
    v = Vision(world, files)

v.run()

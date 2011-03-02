#! /usr/bin/env python
# -*- coding: utf-8 -*-

from vision2.vision import Vision
from common.world import World
import sys

import logging
#logging.basicConfig(level=logging.DEBUG)

args = len(sys.argv)
if args < 1:
    print "Usage: vision.py [filename]"
    sys.exit(2)

world = World()
if args == 1:
    v = Vision(world)
elif args > 1:
    files = sys.argv[1:]
    v = Vision(world, files)

v.run()

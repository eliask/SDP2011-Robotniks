#! /usr/bin/env python
# -*- coding: utf-8 -*-

from simulator2.simulator2 import Simulator
from strategy.strategies import *
import common.world
import simulator2.world as simworld
import getopt, sys
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("simulator2.launcher")

def usage():
    print "Usage: simulator.py <options>"
    print "  -H, --headless  Run without graphical output from simulator"
    print "  -l, --list-strategies  Print the list of available strategies"
    print "  -z, --speed     Set simulator speed (default 1)"
    print "  -s, --strategy1 Use specified strategy for robot 1"
    print "  -t, --strategy2 Use specified strategy for robot 2"
    print "  -S, --real1     Robot 1 operates in the real world"
    print "  -T, --real2     Robot 2 operates in the real world"
    print "  -c, --colour    The colour of robot 1. Blue by default"
    print "  -h, --help      Print this message"

def main():
    try:
        opts, args = \
            getopt.getopt( sys.argv[1:], "Hhz:ls:t:STrc:1:2:",
                           [ "headless", "help", "speed",
                             "list-strategies", "strategy1", "strategy2",
                             "real1", "real2", "colour", "arg1", "arg2",
                             ] )
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        usage()
        sys.exit(2)

    headless = False
    strategy1, strategy2 = None, None
    real1 = real2 = None
    colour = 'blue'
    arg1 = arg2 = None
    speed = 1

    for opt, arg in opts:
        if opt in ("-H", "--headless"):
            headless = True
        if opt in ("-z", "--speed"):
            speed = int(arg)
        elif opt in ("-l", "--list-strategies"):
            list_strategies()
            sys.exit()
        elif opt in ("-s", "--strategy1"):
            strategy1 = arg
        elif opt in ("-t", "--strategy2"):
            strategy2 = arg
        elif opt in ("-S", "--real1"):
            real1 = True
        elif opt in ("-T", "--real2"):
            real2 = True
        elif opt in ("-c", "--colour"):
            colour = arg
        elif opt in ("-1", "--arg1"):
            arg1 = arg
        elif opt in ("-2", "--arg2"):
            arg1 = arg
        elif opt in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"

    ai1 = ai2 = None
    if strategy1:
        ai1 = strategies[strategy1]
    if strategy2:
        ai2 = strategies[strategy2]

    world = simworld.World()

    sim = Simulator( headless=headless,
                     speed=speed,
                     world=world,
                     robot1=(ai1, real1),
                     robot2=(ai2, real2),
                     ai_args=[arg1, arg2],
                     colour=colour,
                     )
    sim.run()

if __name__ == "__main__":
    main()

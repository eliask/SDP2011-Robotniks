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
    print "  -s, --strategy1 Use specified strategy for robot 1"
    print "  -t, --strategy2 Use specified strategy for robot 2"
    print "  -S, --real1     Robot 1 operates in the real world"
    print "  -T, --real2     Robot 2 operates in the real world"
    print "  -h, --help      Print this message"

def main():
    try:
        opts, args = \
            getopt.getopt( sys.argv[1:], "Hhls:t:STrc:",
                           [ "headless", "help",
                             "list-strategies", "strategy1", "strategy2",
                             "real1", "real2", "colour",
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

    for opt, arg in opts:
        if opt in ("-H", "--headless"):
            headless = True
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

    assert colour, "Need to set robot colour"

    # assert not (real1 or real2) or vision, \
    #    "Using real robots requires vision"

    # if real1 or real2:
    #     world = common.world.World(colour)
    # else:
    world = simworld.World(colour)

    assert not (real1 and real2), \
        "How are we to run 2 physical robots??"

    sim = Simulator( headless=headless,
                     world=world,
                     robot1=(ai1, real1),
                     robot2=(ai2, real2),
                     colour=colour,
                     real_world=None, #(real1 or real2),
                     )
    sim.run()

if __name__ == "__main__":
    main()

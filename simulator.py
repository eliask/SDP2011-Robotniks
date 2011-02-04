#! /usr/bin/env python
# -*- coding: utf-8 -*-

from simulator.simulator import *
from simulator.pitch import *
from strategy.strategies import *
import common.world
import simulator.world
import getopt, sys
import logging
logging.basicConfig(level=logging.DEBUG)

def usage():
    print "Usage: simulator.py <options>"
    print "  -H, --headless  Run without graphical output from simulator"
    print "  -V, --vision    Output simulated image to vision"
    print "  -C, --camera    Use an actual camera for the pitch"
    print "  -v, --video     Use a specified video"
    print "  -i, --image     Use a specified image"
    print "  -b, --black     The pitch will be solid black"
    print "  -z, --crazy     The background won't be redrawn"
    print "  -1, --once      Don't loop a video or don't try restarting camera"
    print "  -l, --list-strategies  Print the list of available strategies"
    print "  -s, --strategy1 Use specified strategy for robot 1"
    print "  -t, --strategy2 Use specified strategy for robot 2"
    print "  -S, --real1     Robot 1 operates in the real world"
    print "  -T, --real2     Robot 2 operates in the real world"
    print "  -h, --help      Print this message"

def main():
    try:
        opts, args = \
            getopt.getopt( sys.argv[1:], "HVCv:i:bz1hls:t:STrc:",
                           [ "headless", "vision", "camera", "video",
                             "image", "black", "crazy", "once", "help",
                             "list-strategies", "strategy1", "strategy2",
                             "real1", "real2", "colour",
                             ] )
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        usage()
        sys.exit(2)

    inputs = { 'video'  : None,
               'image'  : None,
               'camera' : False,
               'black'  : False,
               'crazy'  : False,
             }
    once = False
    headless = False
    vision = False
    strategy1, strategy2 = None, None
    real1 = real2 = None
    colour = 'blue'

    for opt, arg in opts:
        if opt in ("-H", "--headless"):
            headless = True
        elif opt in ("-V", "--vision"):
            vision = True
        elif opt in ("-C", "--camera"):
            inputs['camera'] = True
        elif opt in ("-v", "--video"):
            inputs['video'] = arg
        elif opt in ("-i", "--image"):
            inputs['image'] = arg
        elif opt in ("-b", "--black"):
            inputs['black'] = True
        elif opt in ("-z", "--crazy"):
            inputs['crazy'] = True
        elif opt in ("-1", "--once"):
            once = True
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
    world = simulator.world.World(colour)

    assert not (real1 and real2), \
        "How are we to run 2 physical robots??"

    pitch = selectPitch(inputs, once)

    sim = Simulator( pitch=pitch,
                     vision=vision,
                     headless=headless,
                     world=world,
                     robot1=(ai1, real1),
                     robot2=(ai2, real2),
                     colour=colour,
                     real_world=None, #(real1 or real2),
                     )
    sim.run()

def selectPitch(inputs, once):
    selectedInputs = [ k for k,v in inputs.items() if v ]
    if len(selectedInputs) > 1:
        print "Only one pitch input can be used at a time"
        sys.exit(2)
    elif len(selectedInputs) == 0:
        # The default is to use a static background
        name = 'image'
        inputs['image'] = "vision/media/calibrated-background-cropped.png"
    else:
        name = selectedInputs[0]

    if name == 'camera':
        pitch = OpenCVPitch(once=once)
    elif name == 'video':
        pitch = OpenCVPitch(inputs['video'], once=once)
    elif name == 'image':
        pitch = StaticPitch(inputs['image'])
    elif name == 'black':
        pitch = SolidPitch()
    elif name == 'crazy':
        pitch = None
    else:
        assert False, "unknown pitch"

    return pitch

if __name__ == "__main__":
    main()

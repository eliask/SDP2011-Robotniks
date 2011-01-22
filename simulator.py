#! /usr/bin/env python
# -*- coding: utf-8 -*-

from simulator.simulator import *
from simulator.pitch import *
import getopt, sys

def usage():
    print "Usage: simulator.py <options>"
    print "  -H, --headless  Run without graphical output from simulator"
    print "  -V, --vision    Output simulated image to vision"
    print "  -c, --camera    Use an actual camera for the pitch"
    print "  -v, --video     Use a specified video"
    print "  -i, --image     Use a specified image"
    print "  -b, --black     The pitch will be solid black"
    print "  -z, --crazy     The background won't be redrawn"
    print "  -1, --once      Don't loop a video or don't try restarting camera"
    print "  -h, --help      Print this message"

def main():
    try:
        opts, args = \
            getopt.getopt( sys.argv[1:], "HVcv:i:bz1h",
                           [ "headless", "vision", "camera", "video",
                             "image", "black", "crazy", "once", "help" ] )
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

    for opt, arg in opts:
        if opt in ("-H", "--headless"):
            headless = True
        elif opt in ("-V", "--vision"):
            vision = True
        elif opt in ("-c", "--camera"):
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
        elif opt in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"

    pitch = selectPitch(inputs, once)
    sim = Simulator( pitch=pitch,
                     vision=vision,
                     headless=headless )
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

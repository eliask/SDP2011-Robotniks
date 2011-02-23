from communication.interface import *
from common.utils import *
from common.world import *
from math import *
from strategy import *
import logging

class Main(Strategy):
    """The main strategy class

    """
    std = True
    spinning = False
    driving = False
    move_angle = 0

    def __init__(self, *args):
        Strategy.__init__(self, *args)
        self.reset()

    def run(self):
        "Run strategy off of the current state of the World."

        #ballPos=np.array(300,200)
        try:
            self.me = self.world.getSelf() # Find out where I am
        except Exception, e:
            logging.warn("couldn't find self: %s", e)
            return
        try:
            ballPos = self.world.getBall().pos # are we there yet?
        except Exception, e:
            logging.warn("couldn't find ball: %s", e)
            return

        print self.me.pos, ballPos
        if self.me.pos[0] == 0 or ballPos[0] == 0:
            self.stop()
            print "POS 0"
            return

        if self.moveTo( ballPos ): # are we there yet?
            self.kick()

    def moveTo(self, dest):
        logging.debug("moveTo(%s)", pos2string(dest))

        if not self.turnTo(dest):
            #self.stop()
            return False

        print self.me.pos
        _dist = dist(dest, np.array(self.me.pos))
        print _dist
        print dest
        logging.debug("Distance to ball: %.3f" % _dist)
        epsilon = 50
        # TODO: implement the canKick predicate instead
        if _dist < epsilon:
            if self.driving:
                time.sleep(1)
                self.stop()
                self.driving=False
            return True
        else:
            if not self.std:
                self.std = True
                self.reset()
            else:
                self.driving = True
                self.drive()
            return False

    def turnTo(self, dest):
        logging.debug("turnTo(%s)", pos2string(dest))

        # We convert the position of the destination to a coordinate
        # system centered around us. We face the X axis.
        dest2, self2 = rotatePoints([dest, self.me.pos], self.me.pos,
                              -self.me.orientation, new_origin=True)

        print dest, self.me.pos
        print dest2, self2
        assert (self2 <= 2).all(), \
            "the self-centered coordinate system" \
            "should have the self centered on 0"

        x,y = dest2

        angle = atan2(y,x)
        print "Delta-angle:", self.move_angle, angle
        if degrees(abs(self.move_angle - angle)) < 10:
            return True
        else:
            print "Set angle:", angle
            time.sleep(1)
            self.stop()
            time.sleep(1)
            self.setRobotDirection(angle)
            time.sleep(2)
            self.move_angle = angle
            return True

        # Since we are facing x = 0, we choose the turning direction
        # by seeing whether the destination is above or below us

        # self.world.pointer = self.me.pos + \
        #     np.array((cos(closest), sin(closest))) * (dest - self.me.pos)

        epsilon = 10
        if abs(y) < epsilon:
            self.stopSpin()
            self.spinning = False
            return True
        if self.spinning:
            self.std = True
            self.drive()
            return False

        if y > 0:
            #self.spinning = not self.spinning
            self.startSpinLeft()
        else:
            self.startSpinRight()

        self.spinning = True
        return False


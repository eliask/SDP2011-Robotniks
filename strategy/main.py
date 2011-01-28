from .communication.interface import *
from .common.utils import *
from .common.world import *
from math import *
from strategy import *
import logging

class Main(Strategy):
    """The main strategy class

    """

    def run(self):
        "Run strategy off of the current state of the World."

        #ballPos=np.array(300,200)
        try:
            self.me = self.world.getSelf() # Find out where I am
        except:
            logging.warn("couldn't find self")
            return
        try:
            ballPos = self.world.getBall().pos # are we there yet?
        except Exception, e:
            logging.warn("couldn't find self: %s", e)
            raise
            return

        # if self.moveTo( ballPos ): # are we there yet?
        #     self.kick()

    def moveTo(self, dest):
        logging.debug("moveTo(%s)", pos2string(dest))

        if not self.turnTo(dest):
            #self.stop()
            return False

        _dist = dist(dest, self.me.pos)
        logging.debug("Distance to ball: %.3f" % _dist)
        epsilon = 20
        # TODO: implement the canKick predicate instead
        if _dist < epsilon:
            self.stop()
            return True
        else:
            self.reset()
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

        # Since we are facing x = 0, we choose the turning direction
        # by seeing whether the destination is above or below us

        # self.world.pointer = self.me.pos + \
        #     np.array((cos(closest), sin(closest))) * (dest - self.me.pos)

        epsilon = 20
        if abs(y) < epsilon:
            #self.stopSpin()
            return True
        if y > 0:
            if rotAngle < turnThresh:
                self.startSpinLeft()
            else:
                self.drive()
        else:
            self.startSpinRight()
        self.drive()
        return False


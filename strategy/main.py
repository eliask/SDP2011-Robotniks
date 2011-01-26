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
            print "couldn't find self"
            return
        try:
            ballPos = self.world.getBall().pos # are we there yet?
        except Exception, e:
            print "couldn't find ball:",e
            raise
            return

        if self.moveTo( ballPos ): # are we there yet?
            self.kick()

    def moveTo(self, dest):
        logging.debug("moveTo(%s)", pos2string(dest))

        if not self.turnTo(dest):
            self.stop()
            return False

        _dist = dist(dest, self.me.pos)
        logging.debug("Distance to ball: %.3f" % _dist)
        epsilon = 20
        # TODO: implement the canKick predicate instead
        if _dist < epsilon:
            self.stop()
            return True
        else:
            self.drive()
            return False

    def turnTo(self, dest):
        logging.debug("turnTo(%s)", pos2string(dest))

        orient = self.me.orientation

        dx, dy = dest[0] - self.me.pos[0], dest[1] - self.me.pos[1]
        angleToTarget = atan2(dy, dx)

        epsilon = radians(10)
        deltaAngle = angleToTarget - orient

        # TODO: predictive turning--move to the direction that
        # minimises intercept time
        closest = getAnglePi(deltaAngle)
        logging.debug("Angle relative to ball: %.3f" % deltaAngle)

        if abs(deltaAngle) < epsilon:
            self.stopSpin()
            return True
        else:
            if 0 <= deltaAngle <= pi:
                self.startSpinLeft()
            else:
                self.startSpinRight()
            return False


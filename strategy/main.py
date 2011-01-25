from .communication.interface import *
from .common.utils import *
from .common.world import *
from math import *

class Main(Strategy):

    def run(self):
        "Run strategy off of the current state of the World."
        self.kick()
        self.me = self.world.getSelf() # Find out where I am

        if self.moveTo( self.world.getBall().pos ): # are we there yet?
            self.kick()

    def moveTo(self, dest):
        if not self.turnTo(dest):
            return False

        epsilon = 20
        # TODO: implement the canKick predicate instead
        if dist(dest, self.me.pos) < epsilon
            return True
        else:
            return False

    def turnTo(self, dest):
        orient = self.me.orientation
        dx, dy = dest[0] - self.me.pos[0], dest[1] - self.me.pos[1]
        angleToTarget = atan2(dy, dx)

        epsilon = radians(6)
        deltaAngle = angleToTarget - orient

        if abs(deltaAngle) < epsilon:
            return True
        else:
            # TODO: work out the 'closer' direction
            self.startSpinLeft()
            return False


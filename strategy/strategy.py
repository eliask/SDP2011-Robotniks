from .communication.client import Client
from .common.utils import *
from .common.world import *
from math import *

class Strategy(Client):

    def __init__(self, world):
        Client.__init__(self)
        self.world = world

    def run(self):
        "Run strategy off of the current state of the World."
        self.getSelf() # Find out which robot is me
        pos = self.getBallPos()

        if self.moveTo(pos): # are we there yet?
            self.kick()

    def getSelf(self):
        # TODO: resolve the actual self from user input somehow
        self.me = self.world.ents['blue']

    def getBallPos(self):
        ball = self.world.ents['ball']
        return ball.pos

    def getPos(self):
        return self.me.pos

    def moveTo(self, pos):
        if not self.turnTo(pos):
            return False

        epsilon = 15
        if dist(pos, self.getPos()) < epsilon:
            return True
        else:
            return False

    def turnTo(self, pos):
        myPos = self.getPos()
        orient = self.me.orient
        dx, dy = pos[0] - myPos[0], pos[1] - myPos[1]
        angleToTarget = atan2(dy, dx)

        epsilon = radians(6)
        deltaAngle = angleToTarget - orient

        if abs(deltaAngle) < epsilon:
            return True
        else:
            # TODO: work out the 'closer' direction
            self.startSpinLeft()
            return False


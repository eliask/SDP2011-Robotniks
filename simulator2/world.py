from math import *
from pygame.locals import *
import common.world
import numpy as np

class World(common.world.World):

    Friction = 0.03
    scale = 3.0
    offset = 4

    def __init__(self, *args):
        #self.sim = sim
        common.world.World.__init__(self, *args)
        self.name = "Simulated World"
        self.ents = {}

    def setSelf(self, robot):
        self.me = robot
    def setBall(self, ball):
        self.ball = ball

    def convertPos(self, pos):
        return pos
        new = np.array(pos / self.scale - self.offset)
        assert (new <= np.array(self.PitchDim)+10).all()
        return new

    def convertVel(self, vel):
        return vel
        return np.array(vel / self.scale)

    def getSelf(self):
        robot = common.world.Robot()
        robot.pos = self.convertPos(self.me.robot.body.position)
        robot.velocity = self.convertVel(self.me.robot.body.velocity)
        robot.orientation = self.me.robot.body.angle % (2*pi)
        robot.ang_v = self.me.robot.body.angular_velocity
        robot.left_angle = self.me.wheel_left.body.angle % (2*pi)
        robot.right_angle = self.me.wheel_right.body.angle % (2*pi)
        return robot

    def getOpponent(self):
        return self.ents['yellow']

    def openLog(self):
        pass # No anomalies to record

    # def getSelf(self):
    #     return self.us
    # def getOpponent(self):
    #     return self.them
    def getBall(self):
        ball = common.world.Ball()
        ball.pos = self.convertPos( self.ball.body.position )
        ball.velocity = self.convertVel( self.ball.body.velocity )
        ball.ang_v = self.ball.body.angular_velocity
        return ball

    def myPos(self):
        return self.getSelf().pos
    def opponentPos(self):
        return self.getOpponent().pos

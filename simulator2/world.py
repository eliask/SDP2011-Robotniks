from math import *
from pygame.locals import *
import common.world
import numpy as np

class World(common.world.World):

    Friction = 0.03

    def __init__(self, *args):
        common.world.World.__init__(self, *args)
        self.name = "Simulated World"
        self.ents = {}

    def getRobot(self, colour):
        R = self.ents[colour]
        robot = common.world.Robot()
        robot.pos = R.robot.body.position
        robot.velocity = R.robot.body.velocity
        robot.orientation = R.robot.body.angle % (2*pi)
        robot.ang_v = R.robot.body.angular_velocity
        robot.left_angle = R.wheel_left.body.angle % (2*pi)
        robot.right_angle = R.wheel_right.body.angle % (2*pi)
        return robot

    def getBall(self):
        B = self.ents['ball']
        ball = common.world.Ball()
        ball.pos = B.body.position
        ball.velocity = B.body.velocity
        ball.ang_v = B.body.angular_velocity
        return ball

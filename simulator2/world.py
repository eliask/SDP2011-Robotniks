from pygame.locals import *
import common.world

class World(common.world.World):

    Friction = 0.03

    def __init__(self, ourColour):
        common.world.World.__init__(self, ourColour)
        self.name = "Simulated World"
        self.ents = {}

    def setSelf(self, robot):
        self.me = robot
    def setBall(self, ball):
        self.ball = ball

    def getSelf(self):
        robot = common.world.Robot()
        robot.pos = self.me.robot.body.position
        robot.velocity = self.me.robot.body.velocity
        robot.orientation = self.me.robot.body.angle
        robot.ang_v = self.me.robot.body.angular_velocity
        robot.wheel_left = self.me.wheel_left
        robot.wheel_right = self.me.wheel_right
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
        ball.pos = self.ball.body.position
        ball.velocity = self.ball.body.velocity
        ball.ang_v = self.ball.body.angular_velocity
        return ball

    def myPos(self):
        return self.getSelf().pos
    def opponentPos(self):
        return self.getOpponent().pos

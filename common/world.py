from utils import *
import time
from math import *
from robot_estimator import *
from ball_estimator import *

class Robot(object): pass
class Ball(object):  pass

class World(object):
    # Lengths are in millimetres
    PitchWidth   = 121.5
    PitchLength  = 224.0
    BallDiameter = 4.5
    BallRadius   = BallDiameter/2.0
    GoalLength   = 58.5
    RobotLength  = 20.0
    RobotWidth   = 18.0
    KickerReach  = 5.0
    PitchDim     = PitchLength, PitchWidth

    TopWall      = 0.0
    BottomWall   = PitchWidth
    LeftWall     = 0.0
    RightWall    = PitchLength

    max_states   = 5000
    states = []

    vHorizon = 6   # How many past states to use when calculating
                   # velocity
    vWeight  = 0.5 # How much weight to give to the latest 'raw'
                   # velocity vs. the recent past average

    # The entities we are interested in
    entityNames = ('ball', 'blue', 'yellow')

    def __init__(self):
        self.name = "Real World"
        self.time = time.time()

        self.ents = {}
        self.est = { 'ball'   : BallEstimator(),
                     'yellow' : RobotEstimator(),
                     'blue'   : RobotEstimator(),
                     }

    def getResolution(self):
        return self.resolution
    def setResolution(self, res):
        self.resolution = res

        # Left/right goals
        self.GoalPositions = \
            [ (0, self.resolution[1]/2.0),
              (self.resolution[0], self.resolution[1]/2.0),
              ]

    def update(self, time, ents):
        dt = time - self.time
        self.time = time
        self.ents = ents
        self.pointer = None

        self.est['ball'].update( ents['balls'], dt )
        self.est['yellow'].update( ents['yellow'], dt )
        self.est['blue'].update( ents['blue'], dt )

        self.updateStates()

    def getRobot(self, colour):
        est = self.est[colour]
        robot = Robot()
        robot.pos = est.getPos()
        robot.velocity = est.getVelocity()
        robot.orientation = est.getOrientation()
        return robot

    def getGoalPos(self, colour):
        if colour == 'blue':
            return self.GoalPositions[0]
        else:
            return self.GoalPositions[1]

    def swapGoals(self):
        self.GoalPositions = \
            [ self.GoalPositions[1], self.GoalPositions[0] ]


    def getBall(self):
        ball = Ball()
        ball.pos =      self.est['ball'].getPos()
        ball.velocity = self.est['ball'].getVelocity()
        return ball

    def updateStates(self):
        self.ents['time'] = self.time
        self.states.append(self.ents)
        if len(self.states) > self.max_states:
            del self.states[0]

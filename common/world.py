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

        for col in ('blue', 'yellow'):
            self.est[col].text = []
            self.est[col].target = None
            self.est[col].target_time = 0

    def getResolution(self):
        return self.resolution
    def setResolution(self, res):
        self.resolution = res

        # Left/right goals
        self.GoalPositions = \
            [ (0.03*self.resolution[0], self.resolution[1]/2.0),
              (0.97*self.resolution[0], self.resolution[1]/2.0),
              ]

    def update(self, _time, ents):
        dt = _time - self.time
        self.time = _time
        self.ents = ents
        self.pointer = None

        self.est['ball'].update( ents['balls'], dt )
        for colour in ('blue', 'yellow'):
            if self.est[colour].target_time + 1.0 < time.time():
                self.est[colour].target = None
            self.est[colour].update( ents[colour], dt )

        self.ents['time'] = self.time
        self.states.append(self.ents)
        if len(self.states) > self.max_states:
            del self.states[0]

    def getRobot(self, colour):
        est = self.est[colour]
        robot = Robot()
        robot.pos         = est.getPos()
        robot.velocity    = est.getVelocity()
        robot.orientation = est.getOrientation()
        robot.text        = est.text
        robot.target      = est.target
        return robot

    def getGoalPos(self, colour):
        if colour == 'blue':
            return self.GoalPositions[0]
        else:
            return self.GoalPositions[1]

    def getGoalPoints(self, colour):
        center = self.getGoalPos(colour)
        return map( np.array, [(center[0], 0.6*center[1]),
                               (center[0], 1.4*center[1])] )

    def swapGoals(self):
        self.GoalPositions = \
            [ self.GoalPositions[1], self.GoalPositions[0] ]

    def getBall(self):
        ball = Ball()
        ball.pos      = self.est['ball'].getPos()
        ball.velocity = self.est['ball'].getVelocity()
        return ball

    def setTarget(self, colour, target):
        self.est[colour].target = target
        self.est[colour].target_time = time.time()

    def addText(self, colour, line):
        self.est[colour].text.insert(0, line)
        if len( self.est[colour].text ) > 4:
            self.est[colour].text.pop()

    def setStatus(self, text):
        self.status = text

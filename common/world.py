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

    vertical_ratio = 0.05
    horizontal_ratio = 0.04

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
        self.res_scale = 0.83 * res[0]/self.PitchLength
        self.setGoalPositions()

    def setGoalPositions(self):
        h = self.horizontal_ratio
        # Left/right goals
        self.GoalPositions = \
            [ (h*self.resolution[0], self.resolution[1]/2.0),
              ((1-h)*self.resolution[0], self.resolution[1]/2.0),
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
                self.est[colour].text   = []
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

    Poffset = np.array([0,0])
    def getPitchBoundaries(self):
        len_ratio = self.GoalLength / (2*(self.PitchWidth-self.GoalLength))

        v, h = self.vertical_ratio, self.horizontal_ratio
        Gtop1, Gbottom1 = self.getGoalPoints('blue')
        Gtop2, Gbottom2 = self.getGoalPoints('yellow')
        if Gtop1[0] > Gtop2[0]:
            Gtop1, Gtop2 = Gtop2, Gtop1
            Gbottom1, Gbottom2 = Gbottom2, Gbottom1

        goalLen = abs(Gtop1[1] - Gbottom1[1])
        top    = self.Poffset + [Gtop1[0], Gtop1[1] - len_ratio * goalLen]
        bottom = self.Poffset + [Gbottom2[0], Gbottom2[1] + len_ratio * goalLen]

        return [top,bottom]

    def getPitchPoints(self):
        top, bottom = self.getPitchBoundaries()
        return [top, (top[0],bottom[1]), bottom, (bottom[0],top[1])]

    def getGoalPos(self, colour):
        if colour == 'blue':
            return self.GoalPositions[0]
        else:
            return self.GoalPositions[1]

    def getGoalPoints(self, colour):
        center = self.getGoalPos(colour)
        D = self.res_scale * self.GoalLength/2.0
        return [ self.Poffset + [center[0], center[1] - D],
                 self.Poffset + [center[0], center[1] + D] ]

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

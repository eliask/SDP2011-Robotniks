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
    entities = ('ball', 'blue', 'yellow')

    res_scale_mult = 0.9
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
        self.res_scale = self.res_scale_mult * res[0]/self.PitchLength
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
        self.ents['ball'] = self.getBall()

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
        D = 0.95 * self.res_scale * self.GoalLength

        v, h = self.vertical_ratio, self.horizontal_ratio
        G1,G2 = self.getGoalPos('blue'), self.getGoalPos('yellow')
        if G1[0] > G2[0]: G2 = G1

        top    = self.Poffset + [G1[0], G1[1] - D]
        bottom = self.Poffset + [G2[0], G2[1] + D]

        return np.array([top,bottom])

    def getPitchPoints(self):
        top, bottom = self.getPitchBoundaries()
        return [top, (top[0],bottom[1]), bottom, (bottom[0],top[1])]

    def getPitchDecisionBoundaries(self):
        robot_ext = 15
        top, bottom = self.getPitchBoundaries()
        return [top + robot_ext, bottom - robot_ext]

    def getPitchDecisionPoints(self):
        top, bottom = self.getPitchDecisionBoundaries()
        return [top, (top[0],bottom[1]), bottom, (bottom[0],top[1])]

    def getGoalPos(self, colour):
        if colour == 'blue':
            return self.GoalPositions[0]
        else:
            return self.GoalPositions[1]

    def getGoalPoints(self, colour):
        center = self.getGoalPos(colour)
        D = 0.88 * self.res_scale * self.GoalLength/2.0
        return [ self.Poffset + [center[0], center[1] - D],
                 self.Poffset + [center[0], center[1] + D] ]

    def swapGoals(self):
        self.GoalPositions = \
            [ self.GoalPositions[1], self.GoalPositions[0] ]

    def ball_velocity(self):
        N=10
        if len(self.states) < N: return np.array([0,0])

        past = map(lambda x:np.array(x['ball'].pos), self.states[-N:])
        # w=3; n=9
        # gauss1d = np.exp( -0.5 * w/n * np.array(range(-(n-1), n, 2))**2 )
        # gauss1d /= sum(gauss1d)
        # print past
        # smoothed1 = np.convolve(gauss1d, map(lambda x:x[0],past), 'same')
        # smoothed2 = np.convolve(gauss1d, map(lambda x:x[1],past), 'same')
        # print smoothed1, smoothed2
        # smoothed = map(np.array, zip(smoothed1, smoothed2))
        # delta = smoothed[-1] - smoothed[0]

        delta = past[-1] - past[0]
        return delta

    def getBall(self):
        ball = Ball()
        ball.pos      = self.est['ball'].getPos()
        ball.velocity = self.est['ball'].getVelocity()
        ball.velocity = self.ball_velocity()
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

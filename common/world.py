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

    framerate = 25.0
    min_velocity = 10.0
    max_velocity = 200.0

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
        #self.dt = _time - self.time
        self.dt = 1./self.framerate
        self.time = _time
        self.ents = ents
        self.pointer = None

        self.est['ball'].update( ents['balls'], self.dt )
        for colour in ('blue', 'yellow'):
            if self.est[colour].target_time + 1.0 < time.time():
                self.est[colour].target = None
                self.est[colour].text   = []
            self.est[colour].update( ents[colour], self.dt )

        self.ents['time'] = self.time
        self.ents['ball'] = self.getBall()
        for col in ('blue', 'yellow'):
            self.ents['est_'+col] = self.getRobot(col)

        self.ents['ball_trajectory'] = self.__getBallTrajectory()

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
        robot.points      = self.getRobotPoints(robot.pos, robot.orientation)
        return robot

    def getRobotPoints(self, pos, orient):
        W,H = self.res_scale/2. * np.array([self.RobotLength, self.RobotWidth])
        points = [(-W,-H), (W,-H), (W,H), (-W,H)]
        rotated = rotatePoints(points, [0, -7.*self.res_scale], orient)
        points = map(lambda x: pos + np.array(x), rotated)
        return points

    Poffset = np.array([0,0])
    def getPitchBoundaries(self):
        D = 0.95 * self.res_scale * self.GoalLength

        v, h = self.vertical_ratio, self.horizontal_ratio
        G1,G2 = self.getGoalPos('blue'), self.getGoalPos('yellow')
        if G1[0] > G2[0]: G1, G2 = G2, G1

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

    def getBallTrajectory(self):
        N = 3
        def median(z):
            x = sorted(z, key=lambda x:x[0])[int((N-1)/2)][0]
            y = sorted(z, key=lambda x:x[1])[int((N-1)/2)][1]
            return (x,y)
        mean = lambda z: sum(z)/len(z)

        if len(self.states) < N: return self.ents['ball_trajectory']
        past = map(lambda x:np.array(x['ball_trajectory']), self.states[-N:])

        avgs = []
        for i in range(len(past[0])):
            avg = mean( [past[x][i] for x in range(N)] )
            avgs.append(avg)
        return avgs

    def __getBallTrajectory(self):
        ball = self.getBall()
        top, bottom = self.getPitchBoundaries()

        dT = 0.1
        friction = 0.927 ** dT
	maxTime = 5
        maxDist = dist(top, bottom)
	p = 0
        _dist = 0

	posX, posY = ball.pos
	v = np.array( ball.velocity )
        mag = dist(v,[0,0])
        if mag < self.min_velocity:
            v *= 0
        if mag > self.max_velocity:
            v *= self.max_velocity/mag

        trajectory = []
	while p < maxTime:
            v *= friction
            nextPosX = posX + v[0]*dT
            nextPosY = posY + v[1]*dT
            if nextPosX > bottom[0]:
                v[0] = -v[0]
                nextPosX = bottom[0] - (nextPosX - bottom[0])
            if nextPosX < top[0]:
                v[0] = -v[0]
                nextPosX = top[0] - (nextPosX - top[0])
            if nextPosY < top[1]:
                v[1] = -v[1]
                nextPosY = top[1] - (nextPosY - top[1])
            if nextPosY > bottom[1]:
                v[1] = -v[1]
                nextPosY = bottom[1] - (nextPosY - bottom[1])

            posX = nextPosX
            posY = nextPosY
            trajectory.append((posX,posY))
            p += dT
            _dist += dT*sqrt(v[0]**2 + v[1]**2)

        return trajectory

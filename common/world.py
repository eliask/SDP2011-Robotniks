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
    RobotLength  = 22.0
    RobotWidth   = 19.0
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

        self.status = ""
        self.status_time = 0
        self.predict_time = 0
        self.overwrite_ball = None

    def getResolution(self):
        return self.resolution
    def setResolution(self, res):
        self.resolution = res
        self.res_scale = self.res_scale_mult * res[0]/self.PitchLength
        self.ball_dradius = self.res_scale * 24
        self.setGoalPositions()

    def setGoalPositions(self):
        h = self.horizontal_ratio
        # Left/right goals
        self.GoalPositions = \
            [ (h*self.resolution[0], self.resolution[1]/2.0),
              ((1-h)*self.resolution[0], self.resolution[1]/2.0),
              ]

    def update(self, _time, ents):
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
        L,W = self.res_scale/2. * np.array([self.RobotLength, self.RobotWidth])
        O = -3. * self.res_scale
        points = [(-L+O,-W), (L+O,-W), (L+O,W), (-L+O,W)]
        rotated = rotatePoints(points, [0,0], orient)
        rotated = map(lambda x: pos + np.array(x), rotated)
        return rotated

    Poffset = np.array([0,0])
    def getPitchBoundaries(self):
        D = 0.99 * self.res_scale * self.GoalLength

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
        robot_ext = 28
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

        if self.overwrite_ball:
            ball.pos = np.array(self.overwrite_ball)
        else:
            ball.pos = self.est['ball'].getPos()

        if self.predict_time > 0:
            pass

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
        self.status_time = time.time()

    def getStatus(self):
        if self.status_time < time.time() + 0.5:
            self.status = ""
        return self.status

    def getBallDecisionPoints(self, colour):
        ball = self.getBall()
        robot = self.getRobot(colour)
        return self.getCircleTangents(ball.pos,
                                      self.ball_dradius,
                                      robot.pos)

    def getBallGoalCone(self, colour):
        ball = self.getBall()
        top, bottom = self.getGoalPoints( other_colour(colour) )
        dx,dy = ball.pos - top
        top_angle = atan2(dy,dx)
        dx,dy = ball.pos - bottom
        bottom_angle = atan2(dy,dx)
        return top_angle, bottom_angle

    def angleInRange(self, angle1, angle, angle2):
        # NB. Horribly broken
        _angle1 = 0
        _angle2 = (angle2 - angle1) % (2*pi)
        _angle = (angle - angle1) % (2*pi)
        if pi - _angle2 > 0:
            return _angle2 <= _angle <= 2*pi
        else:
            return _angle1 <= _angle <= _angle2

    def getBallGoalPoint(self, colour):
        ball = self.getBall()
        angle = self.getBallGoalDirection( other_colour(colour) )
        point = ball.pos + self.ball_dradius * \
            np.array([cos(angle), sin(angle)])

        return angle, point

    def getBallGoalDirection(self, colour):
        ball = self.getBall()
        dx,dy = ball.pos - self.getGoalPos(colour)
        angle = atan2(dy,dx)
        return angle

    def getCircleTangents(self, circle, radius, point):
        _dist = dist(circle, point)
        if _dist < radius:
            _dist = radius
        angle1 = asin(radius / _dist)

        dx,dy = circle - point
        angle2 = atan2(dy,dx)
        angles = [ angle2 - angle1, angle2 + angle1 ]

        Len = sqrt(_dist**2 - radius**2)
        points = map(lambda x:point+[Len*cos(x),Len*sin(x)], angles)

        return angles, points

    def getBallTrajectory(self, max_time=0):
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

    def __getBallTrajectory(self, max_time=0):
        ball = self.getBall()
        top, bottom = self.getPitchBoundaries()

        dT = 0.1
        friction = 0.78 ** dT
	if max_time == 0:
            max_time = 5.0
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
	while p < max_time:
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

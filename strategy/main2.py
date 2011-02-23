from communication.interface import *
from common.utils import *
from common.world import *
from math import *
from strategy import *
import apf
import mlbridge
import logging
import pygame

class Main2(mlbridge.MLBridge):
    turning_start = 0
    N = 0

    def __init__(self, *args):
        Strategy.__init__(self, *args)
        self.reset()
        self.log = logging.getLogger('strategy.main2')
        self.left_angle = 0
        self.right_angle = 0
        self.until_turned = 0

        self.lock_until = 0
        self.post_lock = lambda:None

    def run(self):
        self.N += 1
        if self.N == 1e100:
            self.maybe_reset_world()
            self.turning_start = 0
            self.N = 0

        if self.lock_until > time.time():
            return
        else:
            self.post_lock()
            self.post_lock = lambda:None

        try:
            self.me = self.world.getSelf() # Find out where I am
            self.log.debug("My position: %s", pos2string(self.me.pos))
        except Exception, e:
            self.log.warn("couldn't find self: %s", e)
            return

        ballPos = np.array(self.world.getBall().pos) # are we there yet?
        # try:
        #     ballPos = self.world.getBall().pos # are we there yet?
        # except Exception, e:
        #     self.log.warn("couldn't find ball: %s", e)
        #     return

        #print self.me.pos, ballPos
        if self.me.pos[0] == 0 or ballPos[0] == 0:
            self.stop()
            print "POS 0"
            return

        def pf(pos):
            v = apf.all_apf( pos, self.world.getResolution(), ballPos,
                             self.world.getGoalPos(), World.BallRadius )

            if self.sim:
                pos = self.me.pos
                v2 = np.array(v) * 5
                delta = map(lambda x:int(round(x)), (pos[0]+v2[0], pos[1]+v2[1]))
                #print pos, delta
                pygame.draw.line(self.sim.screen, (123,0,222,130), pos, delta, 10)
                #pygame.draw.circle(self.sim.screen, (255,50,255,130), delta, 6)

            return np.array(v)

        self.moveTo(self.me.pos + 10*pf(self.me.pos))

        if self.reachesGoal():
            print "REACH"
            self.dash()

        #self.sendMessage()
        return
        self.scoreGoal(ballPos)

    def reachesGoal(self):
        _,Y = self.world.getResolution()
        X,_ = self.world.getGoalPos()
        y1 = 1/3.0 * Y
        y2 = 2/3.0 * Y
        points = [self.me.pos, (X,y1), (X,y2)]

        ball = self.world.getBall().pos
        if dist(self.me.pos, np.array(ball)) > 100 or X-ball[0] > 100:
            return False
        if ball[0] >= self.me.pos:
            return False

        return pointInConvexPolygon(points, ball)

    def canKick(self, target_pos):
	if dist(self.me.pos, target_pos) < 20:
            angle_diff = self.me.orientation % (2*pi)
            - pi - abs( atan2(self.me.pos[1] - target_pos[1],
                              (self.me.pos[0] - target_pos[0])) )

            if angle_diff < radians(13):
                return True

    def scoreGoal(self, ballPos):
        if self.moveTo( ballPos ): # are we there yet?
            self.kick()

    def moveTo(self, dest):
        if not self.turnTo(dest):
            #self.drive_both(0)
            return False

        self.log.debug("moveTo(%s)", pos2string(dest))
        #print dest, self.me.pos, type(dest), type(self.me.pos)
        _dist = dist(dest, self.me.pos)
        #print _dist
        #print dest
        self.log.debug("Distance to target: %.3f" % _dist)
        epsilon = 100

        self.drive_both(3)
        # TODO: implement the canKick predicate instead
        if _dist < epsilon:
            # if self.orientToKick():
            #     self.drive_both(3)
            print "WITHIN DIST"
            return True
        else:
            self.drive_both(3)
            return False

    def turnTo(self, dest):
        angle = atan2(dest[1], dest[0])
        self.log.debug("turnTo(%.1f)", degrees(angle))

        dx,dy = dest - self.me.pos
        angle = atan2(dy,dx)
        orient = self.me.orientation
        delta = angle - orient
        self.steer_both(delta)
        print "steer_both(%.1f)" % degrees(delta)

        d_left = delta - self.left_angle
        d_right = delta - self.right_angle
        #print delta

        if self.until_turned < time.time():
            self.until_turned = time.time() + 0.6
            self.left_angle = self.right_angle = delta
            #print self.until_turned
            d_left = d_right = 0

        if angleDiffWithin(abs(d_left), radians(20)) and \
                angleDiffWithin(abs(d_right), radians(20)):
            #print d_left, d_right
            return True
        else:
            self.drive_both(0)
            return False

    def dash(self):
        if True or self.orientToKick():
            self.lock_until = time.time() + 1.8
            self.post_lock = self.kick
            self.drive_both(3)

    def orientToKick(self):
        self.log.debug("orientToKick()")

        ball = self.world.getBall().pos
        goal = self.world.getGoalPos()
        dx,dy = goal[0]-ball[0], goal[1]-ball[1]
        angle = atan2(dy,dx)
        delta = abs(angle - self.me.orientation) % (2*pi)
        self.log.debug( "Difference between orientation and kicking angle: %.1f",
                        degrees(delta) )

        if angleDiffWithin(delta, radians(30)):
            self.turning_start = 0
            self.drive_both(0)
            print "ORIENTED"
            return True
        else:
            if self.turning_start == 0:
                self.turning_start = time.time()
                self.drive_both(0)

            self.steer_left(radians(135))
            self.steer_right(radians(-45))
            if time.time() - self.turning_start > 0.7:
                #print time.time() - self.turning_start
                self.drive_both(3)
            return False

    def orient(angle):
        """Change the robot's orientation to specified angle.

        The robot will be turned in a way that minimises the turning
        time, taking into account wheel turning direction and driving
        direction.
        """
        pass

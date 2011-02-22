from communication.interface import *
from common.utils import *
from common.world import *
from math import *
from strategy import *
import apf
import mlbridge
import logging

class Main2(mlbridge.MLBridge):
    turning_start = 0
    N = 0
    # apf_scale = 0.5
    # apf_dist = 60

    def __init__(self, *args):
        Strategy.__init__(self, *args)
        self.reset()
        self.log = logging.getLogger('strategy.main2')

    def run(self):
        self.N += 1
        if self.N == 1e100:
            self.maybe_reset_world()
            self.turning_start = 0
            self.N = 0

        try:
            self.me = self.world.getSelf() # Find out where I am
            self.log.debug("My position: %s", pos2string(self.me.pos))
        except Exception, e:
            self.log.warn("couldn't find self: %s", e)
            return

        ballPos = self.world.getBall().pos # are we there yet?
        try:
            ballPos = self.world.getBall().pos # are we there yet?
        except Exception, e:
            self.log.warn("couldn't find ball: %s", e)
            return

        #print self.me.pos, ballPos
        if self.me.pos[0] == 0 or ballPos[0] == 0:
            self.stop()
            print "POS 0"
            return

        def pf(pos):
            v = apf.all_apf( pos, ballPos, self.world.getGoalPos(),
                              World.BallRadius )
            return np.array(v)

        self.moveTo(self.me.pos + 100*pf(self.me.pos))

	if self.canKick(ballPos):
		self.kick()

        #self.sendMessage()
        return
        self.scoreGoal(ballPos)

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
        epsilon = 25

        self.drive_both(3)
        # TODO: implement the canKick predicate instead
        if _dist < epsilon:
            return self.orientToKick()
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
        # print "Set angle:", getAnglePi(angle - self.me.left_angle), \
        #     getAnglePi(angle - self.me.right_angle)
        self.steer_both(delta)

        #print "LEFT,RIGHT:", delta, angle, self.me.left_angle, self.me.right_angle

        d_left = abs(angle - self.me.left_angle)
        d_right = abs(angle - self.me.right_angle)
        if angleDiffWithin(d_left, radians(20)) and \
                angleDiffWithin(d_right, radians(20)):
            return True
        else:
            self.drive_both(0)
            return False

    def orientToKick(self):
        self.log.debug("orientToKick()")

        ball = self.world.getBall().pos
        goal = self.world.getGoalPos()
        dx,dy = goal[0]-ball[0], goal[1]-ball[1]
        angle = atan2(dy,dx)
        delta = abs(angle - self.me.orientation) % (2*pi)
        self.log.debug( "Difference between orientation and kicking angle: %.1f",
                        degrees(delta) )

        if angleDiffWithin(delta, radians(20)):
            self.turning_start = 0
            self.drive_both(0)
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

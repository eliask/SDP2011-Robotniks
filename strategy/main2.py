from communication.interface import *
from common.utils import *
from common.world import *
from math import *
from strategy import *
import mlbridge
import logging

class Main2(mlbridge.MLBridge):
    move_angle = 0
    N = 0

    def __init__(self, *args):
        Strategy.__init__(self, *args)
        self.reset()

    def run(self):
        self.N += 1
        if self.N == 40:
            self.maybe_reset_world()
            self.N = 0

        #ballPos=np.array(300,200)
        try:
            self.me = self.world.getSelf() # Find out where I am
        except Exception, e:
            logging.warn("couldn't find self: %s", e)
            return
        try:
            ballPos = self.world.getBall().pos # are we there yet?
        except Exception, e:
            logging.warn("couldn't find ball: %s", e)
            return

        #print self.me.pos, ballPos
        if self.me.pos[0] == 0 or ballPos[0] == 0:
            self.stop()
            print "POS 0"
            return

        self.scoreGoal(ballPos)

    def scoreGoal(self, ballPos):
        if self.moveTo( ballPos ): # are we there yet?
            self.kick()

    def moveTo(self, dest):
        logging.debug("moveTo(%s)", pos2string(dest))

        if not self.turnTo(dest):
            self.drive_both(0)
            return False

        #print self.me.pos
        _dist = dist(dest, np.array(self.me.pos))
        #print _dist
        #print dest
        logging.debug("Distance to ball: %.3f" % _dist)
        epsilon = 50

        # TODO: implement the canKick predicate instead
        if _dist < epsilon:
            return True
        else:
            self.drive_both(3)
            return False

    def turnTo(self, dest):
        logging.debug("turnTo(%s)", pos2string(dest))

        dx,dy = dest - self.me.pos
        angle = atan2(dy,dx)

        orient = self.me.orientation
        delta = angle - orient
        # print "Set angle:", getAnglePi(angle - self.me.left_angle), \
        #     getAnglePi(angle - self.me.right_angle)
        self.steer_both(delta)
        # self.move_angle = angle

        print "LEFT,RIGHT:", delta, angle, self.me.left_angle, self.me.right_angle

        d_left = abs(angle - self.me.left_angle)
        d_right = abs(angle - self.me.right_angle)
        if (d_left < radians(20) or d_left > radians(340)) and \
                (d_right < radians(20) or d_right > radians(340)):
            return True

        return False

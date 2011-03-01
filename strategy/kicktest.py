from communication.interface import *
from common.utils import *
from common.world import *
from math import *
from strategy import Strategy
import logging
import pygame
import common.world

class KickTest(Strategy):
    "A basic module for testing the kicker"

    def __init__(self, *args):
        Strategy.__init__(self, *args)
        self.reset()
        self.log = logging.getLogger('strategy.main2')

        # Variables for tracking the robot's internal state
        self.left_angle = 0
        self.right_angle = 0
        self.until_turned = 0

    def run(self):
        try:
            self.me = self.getSelf() # Find out where I am
        except Exception, e:
            logging.warn("couldn't find self: %s", e)
            return
        try:
            ballPos = self.world.getBall().pos # are we there yet?
        except Exception, e:
            logging.warn("couldn't find ball: %s", e)
            return


        if self.me.pos[0] == 0 or ballPos[0] == 0:
            self.stop()
            print "POS 0"
            return

	if self.canKick(ballPos):
		self.kick()

	v = self.getVirtualBalls(ballPos)
	self.moveTo(v[2])
	if dist(self.me.pos, v[1]) < 10:
		self.drive_both(0)
	
    def canKick(self, target_pos):
	#	to get the angle between [-pi, pi]
	if self.me.orientation > pi:
		self.me.orientation -= 2*pi

	if dist(self.me.pos, target_pos) < 50:
           	angle_diff = self.me.orientation - atan2(target_pos[1] - self.me.pos[1],
                              (target_pos[0] - self.me.pos[0]))
		if angle_diff > pi:
			angle_diff -= 2*pi
		elif angle_diff < -pi:
			angle_diff += 2*pi

            	if abs(angle_diff) < radians(35):
                	return True


    def getVirtualBalls(self, ballPos):
	pos = self.me.pos
	goalPos = self.world.getGoalPos(self.colour)
	offset = 40
	a = (goalPos[1] - ballPos[1]) / (goalPos[0] - ballPos[0])
	b = ((ballPos[1]*goalPos[0]) - (goalPos[1]*ballPos[0]))	/ (goalPos[0] - ballPos[0])
	pygame.draw.line(self.sim.screen, (123,0,222,130), goalPos, ballPos, 2)		
	
	if a == 0:
		p1 = (ballPos[0], 0)
		p2 = (ballPos[0], 8 * World.PitchWidth)
		v1 = (ballPos[0], ballPos[1] - offset)
		v2 = (ballPos[0], ballPos[1] + offset)
		v3 = (ballPos[0] - offset, ballPos[1])
	else:
		a2 = -1/a
		b2 = ballPos[1] - a2*ballPos[0]
	
		y1 = 0
		x1 = (y1 - b2) / a2
		p1 = (x1, y1)

		y2 = 8 * World.PitchWidth
		x2 = (y2 -b2) / a2
		p2 = (x2, y2)

		y3 = ballPos[1] - offset
		x3 = (y3 - b2) / a2
		v1 = (x3, y3)	
		
		y4 = ballPos[1] + offset
		x4 = (y4 - b2) / a2
		v2 = (x4, y4)	
		
		x5 = ballPos[0] - offset
		y5 = a*x5 + b
		v3 = (x5, y5)

	pygame.draw.line(self.sim.screen, (123,0,222,130), p1, p2, 2)		
	pygame.draw.circle(self.sim.screen, (123,0,222,130), v1, 5, 5)
	pygame.draw.circle(self.sim.screen, (123,0,222,130), v2, 5, 5)
	pygame.draw.circle(self.sim.screen, (123,0,222,130), v3, 5, 5)
	return [v1, v2, v3]

    def moveTo(self, dest):
        """Move to the destination

        moveTo requires than the wheels are both pointing towards the
        wanted destination. If they are, turning is stopped and
        driving commands are issued.
        """
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
            if self.orientToKick():
                self.drive_both(3)
            return True
        else:
            self.drive_both(3)
            return False


    def turnTo(self, dest):
        """Turn to make the _wheels_ face the destination.

        This makes the robot turn its wheels until the estimated
        orientation of both wheels is about the same as the angle to
        the destination. While the wheels are turning, the robot will
        not drive.
        """
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

    def orientToKick(self):
        """Orient the robot's body to face the ball.

        The robot will first orient the wheels to a position that allows
        """
        self.log.debug("orientToKick()")

        ball = self.world.getBall().pos
        goal = self.world.getGoalPos(self.colour)
        dx,dy = goal[0]-ball[0], goal[1]-ball[1]
        angle = atan2(dy,dx)
        delta = abs(angle - self.me.orientation) % (2*pi)
        self.log.debug( "Difference between orientation and kicking angle: %.1f",
                        degrees(delta) )

        if angleDiffWithin(delta, radians(40)):
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

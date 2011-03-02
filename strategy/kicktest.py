from communication.interface import *
from common.utils import *
from common.world import *
from math import *
from strategy import Strategy
from main2 import Main2
import logging
import pygame
import common.world

class KickTest(Main2):
    "A basic module for testing the kicker"

    def __init__(self, *args):
        Main2.__init__(self, *args, name='kicktest')

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
	goalPos = self.getOpponentGoalPos()
	offset = 40
	a = (goalPos[1] - ballPos[1]) / (goalPos[0] - ballPos[0])
	b = (ballPos[1]*goalPos[0] - goalPos[1]*ballPos[0]) \
            / (goalPos[0] - ballPos[0])

        res = self.world.getResolution()

	if a == 0:
		p1 = (ballPos[0], 0)
		p2 = (ballPos[0], res[1])
		v1 = (ballPos[0], ballPos[1] - offset)
		v2 = (ballPos[0], ballPos[1] + offset)
		v3 = (ballPos[0] - offset, ballPos[1])
	else:
		a2 = -1/a
		b2 = ballPos[1] - a2*ballPos[0]

		y1 = 0
		x1 = (y1 - b2) / a2
		p1 = (x1, y1)

		y2 = res[1]
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

        if self.sim:
            pygame.draw.line(self.sim.screen, (123,0,222,130), goalPos, ballPos, 2)
            pygame.draw.line(self.sim.screen, (123,0,222,130), p1, p2, 2)
            pygame.draw.circle(self.sim.screen, (123,0,222,130), v1, 5, 5)
            pygame.draw.circle(self.sim.screen, (123,0,222,130), v2, 5, 5)
            pygame.draw.circle(self.sim.screen, (60,60,255,130), v3, 5, 5)

	return [v1, v2, v3]


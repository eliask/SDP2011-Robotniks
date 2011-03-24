from common.utils import *
from common.world import *
from communication.interface import *
from math import *
from strategy import *
import apf
import logging
import pygame

class PenaltyD(Strategy):
    turning_start = 0
    direction = 0
    angle = -90
    opponent_angle = 0

    def __init__(self, *args):
        Strategy.__init__(self, *args, name='penaltydef')

    def run(self):
        try:
            self.me = self.getSelf() # Find out where I am
            #self.log.debug("My position: %s", pos2string(self.me.pos))
        except Exception, e:
            self.log.warn("couldn't find self: %s", e)
            return

        ballPos = np.array( self.world.getBall().pos )
	ball_y = ballPos[1]
	self.turned = 0
	opponent = self.getOpponent()
	opp_angle = degrees(opponent.orientation)
	change = 0

	if self.opponent_angle == 0:
		self.opponent_angle = opp_angle
	else:
		change = self.opponent_angle - opp_angle

	# Turn both wheels
	"""if self.turning_start == 0:
                self.turning_start = time.time()
                self.drive_both(0)
		if self.me.pos[0] > 400:
			self.angle = 90
	if time.time() - self.turning_start < 0.3:
		self.steer_both(radians(self.angle))
	else:"""
	self.turned = 1
	
	# Protect the gate
	if self.turned == 1:
		# check which side we are defending
		if self.me.pos[0] >= 200:
			direction = 1
		else:
			direction = -1
		
		if direction == -1:
			if change < -3:
				self.driveUp()
			if change > 3:
				self.driveDown()

		if direction == 1:
			if change > 3:
				self.driveUp()
			if change < -3:
				self.driveDown()

    def driveUp(self):
	if self.me.pos[1] > 180:
		self.drive_both(3)
	else:
		self.drive_both(0)

    def driveDown(self):
	if self.me.pos[1] < 210:
		self.drive_both(-3)
	else:
		self.drive_both(0)

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

    def __init__(self, *args):
        Strategy.__init__(self, *args)
        self.reset()
        self.log = logging.getLogger('strategy.main2')

        # Variables for tracking the robot's internal state
        self.left_angle = 0
        self.right_angle = 0
        self.until_turned = 0

    def run(self):
        self.getSelf()
        try:
            self.me = self.getSelf() # Find out where I am
            #self.log.debug("My position: %s", pos2string(self.me.pos))
        except Exception, e:
            self.log.warn("couldn't find self: %s", e)
            return

        ballPos = np.array( self.world.getBall().pos )
	ball_y = ballPos[1]
	self.turned = 0	

	if self.turning_start == 0:
                self.turning_start = time.time()
                self.drive_both(0)
	if time.time() - self.turning_start < 0.3:
		self.steer_both(radians(-90)) 
	else:
		self.turned = 1
	
	if self.turned == 1:
		if self.direction == 0:
			if self.me.pos[1] > 170:
				self.drive_both(3)
			else:
				self.drive_both(0)
				self.direction = 1
		else:
			if self.me.pos[1] < 200:
				self.drive_both(-3)
			else:
				self.drive_both(0)
				self.direction = 0

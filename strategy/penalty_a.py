from common.utils import *
from common.world import *
from communication.interface import *
from math import *
from strategy import *
import apf
import logging
import pygame

# Penalty attack strategy
class PenaltyA(Strategy):
    turning_start = 0

    def __init__(self, *args):
        Strategy.__init__(self, *args)
        self.reset()
        self.log = logging.getLogger('strategy.penaltykick')

    def run(self):
        self.getSelf()
        try:
            self.me = self.getSelf() # Find out where I am
            #self.log.debug("My position: %s", pos2string(self.me.pos))
        except Exception, e:
            self.log.warn("couldn't find self: %s", e)
            return

        ballPos = np.array( self.world.getBall().pos )

        opponent = self.getOpponent()

	# Decide which direction to kick
	opp_y = opponent.pos[1]
	if opp_y >= 200:
		direction = 1
	else:
		direction = -1

	# Perform turning and kicking
       	if self.turning_start == 0:
                self.turning_start = time.time()
                self.drive_both(0)
	if time.time() - self.turning_start < 0.2:
		self.drive_left(direction)
		self.drive_right(-direction)
	else:
		self.drive_both(0)
		if time.time() - self.turning_start > 0.5:
			if self.canKick(ballPos):
				self.kick()


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


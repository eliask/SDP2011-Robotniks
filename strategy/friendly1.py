from communication.interface import *
from common.utils import *
from common.world import *
from math import *
from strategy import Strategy
from main2 import Main2
import logging
import pygame
import common.world

class Friendly1(Main2):
    "A basic module for testing the kicker"

    def __init__(self, *args):
        Main2.__init__(self, *args, name='friendly1')

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
        if self.watch_stuck(): return

        if self.me.pos[0] == 0 or ballPos[0] == 0:
            self.drive_both(0)
            print "POS 0"
            return

	if self.canKick(ballPos):
		self.kick()

	left,right,behind = self.getVirtualBalls(ballPos)

        dest = behind
	pos = self.me.pos
        distL, distR = dist(self.me.pos, left), dist(self.me.pos, right)
        distB = dist(self.me.pos, behind)

        if distB < distL and distB < distR:
            # Keep the previous destination if we're closer to it than
            # the auxiliary ones. This happens when we are close to
            # the ball or when we can go straight towards the ball.
            pass

        elif (right[0] - pos[0])*(left[1] - pos[1]) \
                - (right[1] - pos[1])*(left[0] - pos[0]) < 0:
            # We're on the wrong side of the line that divides the
            # ball and the target goal 'decision boundary'.

            if distL < distR:
                dest = left
            else:
                dest = right

        if self.sim:
            pygame.draw.circle(self.sim.screen, (60,60,255,130), dest, 15, 3)

        if dest == behind and distB < 50:
            # If we are close enough to the ball, just switch to
            # potential field guidance. Much larger thresholds will
            # result in much lower performance.
            self.moveTo(pos + 10*self.pf(pos))
        else:
            self.moveTo(dest)

        #self.moveTo(dest)
	# if dist(self.me.pos, behind) < 25:
        #     self.dash()

    def getVirtualBalls(self, ball_pos):
	goal_pos = self.getOpponentGoalPos()
	a = (goal_pos[1] - ball_pos[1]) / (goal_pos[0] - ball_pos[0])
	b = (ball_pos[1]*goal_pos[0] - goal_pos[1]*ball_pos[0]) \
            / (goal_pos[0] - ball_pos[0])

        res = self.world.getResolution()

        Gx,Gy = goal_pos[0]-ball_pos[0], goal_pos[1]-ball_pos[1]
        angle = atan2(Gy,Gx)

	offset = 50
        offset2 = 30
        G1x = ball_pos[0] - offset*sin(angle) - offset2*cos(angle)
        G1y = ball_pos[1] + offset*cos(angle) - offset2*sin(angle)

        G2x = ball_pos[0] + offset*sin(angle) - offset2*cos(angle)
        G2y = ball_pos[1] - offset*cos(angle) - offset2*sin(angle)

        G1 = G1x, G1y
        G2 = G2x, G2y

        G3x = ball_pos[0] - offset*cos(angle)
        G3y = ball_pos[1] - offset*sin(angle)
        G3 = G3x, G3y

        v1, v2, v3 = G1, G2, G3

        if self.sim:
            pygame.draw.circle(self.sim.screen, (123,0,222,130), v1, 5, 5)
            pygame.draw.circle(self.sim.screen, (123,0,222,130), v2, 5, 5)
            pygame.draw.circle(self.sim.screen, (60,60,255,130), v3, 5, 5)

	return [v1, v2, v3]


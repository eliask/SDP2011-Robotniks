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

        if self.intercept():
            print "INTERCEPT"
            return

	vballs = self.getVirtualBalls(ballPos)
        left,right,behind = vballs

        dest = behind
	pos = self.me.pos
        distL, distR = dist(self.me.pos, left), dist(self.me.pos, right)
        distB = dist(self.me.pos, behind)

        oobs = map(self.out_of_bounds, vballs)
        oobL, oobR, oobB = oobs
        if not False in oobs:
            print "BALL STUCK"
            return self.defensive()

        if distB < distL and distB < distR \
                and not oobB:
            # Keep the previous destination if we're closer to it than
            # the auxiliary ones. This happens when we are close to
            # the ball or when we can go straight towards the ball.
            pass

        elif (right[0] - pos[0])*(left[1] - pos[1]) \
                - (right[1] - pos[1])*(left[0] - pos[0]) < 0:
            # We're on the wrong side of the line that divides the
            # ball and the target goal 'decision boundary'.

            if oobL and oobR:
                left = right = behind
            elif oobL:
                left = right
            elif oobR:
                right = left

            if distL < distR:
                dest = left
            else:
                dest = right

        if self.sim:
            pygame.draw.circle(self.sim.screen, (60,60,255,130), dest, 15, 3)

        if dest == behind and distB < 100:
            # If we are close enough to the ball, just switch to
            # potential field guidance. Much larger thresholds will
            # result in much lower performance.
            if self.orientToKick():
                self.moveTo(ballPos) # + 10*self.pf(pos))
        else:
            self.moveTo(dest)

        #self.moveTo(dest)
	# if dist(self.me.pos, behind) < 25:
        #     self.dash()

    def out_of_bounds(self, p):
        top, bottom = self.world.getPitchDecisionBoundaries()
        #print top, bottom, p
        return p[0] < top[0] or p[0] > bottom[0] \
            or p[1] < top[1] or p[1] > bottom[1]

    def out_of_bounds2(self, p):
        top, bottom = self.world.getPitchBoundaries()
        return p[0] < top[0] or p[0] > bottom[0] \
            or p[1] < top[1] or p[1] > bottom[1]

    def intercept(self):
        ball = self.world.getBall()
        v = ball.velocity
        dpos = np.array(self.me.pos) - ball.pos
        if self.out_of_bounds2(ball.pos) or \
                dpos[0] == 0 or dist(v, [0,0]) < 33:
            return False

        angle = atan2(v[1], v[0])
        Y = dpos[0] * sin(angle)
        top, bottom = self.world.getPitchDecisionBoundaries()
        projected = self.me.pos[0], max(top[1], min(bottom[1], Y))

        self.setTarget(projected)

        if v[0] * dpos[0] > 0 and abs(dpos[0]) > 12:
            self.moveTo(projected)
            return True
        else:
            return False

    def boundLegalMove(self, dest):
        top, bottom = self.world.getPitchDecisionBoundaries()
        bounded = np.array( self.me.pos[:] )
        for i in range(2):
            bounded[i] = max(top[i], min(bottom[i], dest[i]))
        return bounded

    def defensive(self):
        ball = self.world.getBall()
        self.moveTo(ball.pos)

    def moveTo(self, dest):
        bounded = self.boundLegalMove(dest)
        super(Friendly1, self).moveTo(bounded)

    def getVirtualBalls(self, ball_pos):
	goal_pos = self.getOpponentGoalPos()
	a = (goal_pos[1] - ball_pos[1]) / (goal_pos[0] - ball_pos[0])
	b = (ball_pos[1]*goal_pos[0] - goal_pos[1]*ball_pos[0]) \
            / (goal_pos[0] - ball_pos[0])

        res = self.world.getResolution()

        Gx,Gy = goal_pos[0]-ball_pos[0], goal_pos[1]-ball_pos[1]
        angle = atan2(Gy,Gx)

	offset = 50
        offset2 = 50
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


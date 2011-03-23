from communication.interface import *
from common.utils import *
from common.world import *
from math import *
from strategy import Strategy
from main2 import Main2
import logging
import pygame
import common.world

class Final(Main2):

    def __init__(self, *args):
        Main2.__init__(self, *args, name='final')

    def run(self):
        try:
            self.me = self.getSelf() # Find out where I am
        except Exception, e:
            logging.warn("couldn't find self: %s", e)
            return

        ballPos = self.world.getBall().pos
        if self.me.pos[0] == 0 or ballPos[0] == 0:
            self.drive_both(0)
            print "Ball or self at 0: doing nothing"
            return

        #if self.watch_stuck(): return

	if self.canKick():
            self.kick()

        if self.intercept():
            print "INTERCEPT"
            return

        D = self.getBallDecisionPoints()
        gpoint = self.getBallGoalPoint()
        oobs = map(self.out_of_bounds, D+[gpoint])

        print oobs
        if not False in oobs:
            print "BALL STUCK"
            return self.defensive()

        if oobs[-1]: del gpoint
        if oobs[1]: del D[1]
        if oobs[0]: del D[0]

        _dist1 = dist(self.me.pos, D[0])
        _dist2 = dist(self.me.pos, D[1])
        _distG = dist(self.me.pos, gpoint)
        print _dist1, _dist2, _distG
        if gpoint and _distG < _dist1 and _distG < _dist2:
            return self.targetBall()

        goal = self.getOpponentGoalPos()
        if D[1] and _dist1 > _dist2:
            self.moveTo(D[1])
        else:
            self.moveTo(D[0])

    def targetBall(self):
        ball = self.world.getBall()
        self.moveTo(ball)

    def canKick(self):
        ball = self.world.getBall().pos
        orient = self.me.orientation
	if dist(self.me.pos, ball) < 50:
            dx,dy = ball - self.me.pos
            delta = orient - atan2(dy,dx)
            delta = atan2(sin(delta), cos(delta))
            if abs(delta) < radians(35):
                return True

    def out_of_bounds(self, p):
        top, bottom = self.world.getPitchDecisionBoundaries()
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
        Y = ball.pos[1] + dpos[0] * sin(angle)
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
        super(Final, self).moveTo(bounded)

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


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

        ball = self.world.getBall()
        if self.me.pos[0] == 0 or ball.pos[0] == 0:
            self.drive_both(0)
            print "Ball or self at 0: doing nothing"
            return

        #if self.watch_stuck(): return

	if self.canKick():
            self.kick()

        # if self.intercept():
        #     print "INTERCEPT"
        #     return

        Dang, Dp = self.getBallDecisionPoints()
        Gang, Gp = self.getBallGoalPoint()
        oobs = map(self.out_of_bounds2, Dp+[Gp])

        my_goal = self.getMyGoalPos()
        goal = self.getOpponentGoalPos()
        if self.out_of_bounds(self.me.pos):
            self.moveTo( np.array([self.me.pos[0], goal[1]]) )

        if not False in oobs:
            self.addText("OOB defensive")
            return self.defensive()

        _ball_dist = self.dist(ball.pos)

        opp = self.getOpponent()
        _opponent_is_far = self.dist(opp.pos) > 200

        _goal_is_far = self.dist(goal) > 2.5 * self.world.ball_dradius

        ball_dist_thresh = 3/2. * self.world.ball_dradius
        _ball_is_far = _ball_dist > ball_dist_thresh
        _opponent_near_ball = dist(opp.pos, ball.pos) <= ball_dist_thresh

        _behind_precisely = False and self.world.angleInRange(Dang[0], Gang, Dang[1])

        _behind_general_dir = \
            (ball.pos[0] - Gp[0]) * (ball.pos[0] - self.me.pos[0]) >= 0 \
            and abs(ball.pos[0] - self.me.pos[0]) > 40 \
            or _behind_precisely

        # if _ball_is_far:
        #     if _opponent_near_ball:
        #         self.addText("defensive")
        #         return self.defensive()
        #     else:
        #         self.addText("opponent far move")
        #         return self.moveTo(Gp)

        ### ball is near ###

        if _behind_precisely:
            self.addText("behind precisely")
            return self.moveTo(ball.pos)

        ### not _behind_precisely ###

        if not _behind_general_dir:
            self.addText("nearest tangent")
            return self.nearestTangent()

        ### _behind_general_dir ###
        self.addText("behind general")

        if False and _opponent_near_ball:
            self.addText("opponent near def")
            return self.defensive()

        ### opponent is far from ball ###

        if not _goal_is_far:
            self.addText("goal near")
            self.moveTo(Gp)

        ### goal is far ###


        ### failing EVERYTHING ###
        self.addText("fallback")
        self.moveTo(ball.pos)

    def nearestTangent(self):
        ball = self.world.getBall()
        if self.world.ball_dradius >= self.dist(ball.pos):
            _dist_ball = self.dist(ball.pos)
            innerR = max(1,min(_dist_ball, 3/4.*self.world.ball_dradius))

            dx,dy = ball.pos - self.me.pos
            angle = atan2(dy,dx)
            inner_tan = ball.pos + innerR * np.array([cos(-angle), sin(-angle)])
            tan_normals = [ [sin(angle), cos(angle)], [sin(-angle), cos(-angle)] ]

            # NB. approximation
            deltaR = self.world.ball_dradius - innerR
            tan_normals = map(lambda x:inner_tan+innerR*np.array(x), tan_normals)
            Gang, Gp = self.getBallGoalPoint()

            D = map(lambda x:dist(Gp, x), tan_normals)
            if D[0] < D[1]:
                return self.moveTo(tan_normals[0])
            else:
                return self.moveTo(tan_normals[1])

        Dang, Dp = self.getBallDecisionPoints()
        oobs = map(self.out_of_bounds2, Dp)
        if oobs[0]: return self.moveTo(Dp[1])
        if oobs[1]: return self.moveTo(Dp[0])

        _dist0 = self.dist(Dp[0])
        _dist1 = self.dist(Dp[1])

        if _dist1 > _dist0:
            return self.moveTo(Dp[0])
        else:
            return self.moveTo(Dp[1])

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

    def carefulKick(self):
        self.orientToKick()
        # ball = self.getBall()
        # #if not self.oriented(): self.orientTo(ball.pos)
        # else: self.moveTo(ball.pos)

    def intercept2(self):
        "Intercept using projected ball trajectories"
        pass

    def intercept(self):
        ball = self.world.getBall()
        v = ball.velocity
        dpos = np.array(self.me.pos) - ball.pos
        if self.out_of_bounds2(ball.pos) or \
                dpos[0] == 0 or dist(v, [0,0]) < 33:
            return False

        angle = atan2(v[1], v[0])
        Y = ball.pos[1] - dpos[0] * sin(angle)
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
        self.world.setStatus("DEFEND")
        ball = self.world.getBall()
        midpoint = (ball.pos + self.getMyGoalPos()) / 2.
        self.moveTo(midpoint)

    def moveTo(self, dest, force=False):
        bounded = self.boundLegalMove(dest)
        super(Final, self).moveTo(bounded, force)

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


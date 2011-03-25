from common.utils import *
from common.world import *
from communication.interface import *
from math import *
from strategy import *
import apf
import logging
import pygame
from main2 import Main2

# Penalty attack strategy
class PenaltyA(Main2):

    def __init__(self, *args):
        Main2.__init__(self, *args, name='penaltykick')
        self.back = False

    def run(self):
        # if self.lock_until > time.time():
        #     return
        # else:
        #     if self.post_lock(): return
        #     self.post_lock = lambda:None

        try:
            self.me = self.getSelf() # Find out where I am
            #self.log.debug("My position: %s", pos2string(self.me.pos))
        except Exception, e:
            self.log.warn("couldn't find self: %s", e)
            return

        ballPos = self.world.getBall().pos

        opponent = self.getOpponent()

        gp = self.getOpponentGoalPoints()

        p = self.world.getRobotPoints(opponent.pos, opponent.orientation)
        s = sorted(p, key=lambda x:x[1])
        high = s[0][1]
        low = s[-1][1]

        if gp[0][1] - high > gp[1][1] - low:
            target = (gp[0][1] + high)/2.
        else:
            target = (gp[1][1] + low)/2.

        dx,dy = target - self.me.pos
        angle = atan2(dy,dx)
        R = 60
        target2 = self.me.pos + R*np.array([cos(angle), sin(angle)])

        if not self.back and self.dist(target2) < R/2.:
            self.back = True
        elif self.back:
            if self.orientToKick(ball.pos) and self.moveTo(ball.pos):
                self.kick()
        else:
            self.moveTo(target2)


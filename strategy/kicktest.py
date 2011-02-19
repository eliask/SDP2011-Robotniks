from communication.interface import *
from common.utils import *
from common.world import *
from math import *
from strategy import Strategy
import logging

class KickTest(Strategy):
    "A basic module for testing the kicker"

    def run(self):
        try:
            self.me = self.world.getSelf() # Find out where I am
        except Exception, e:
            logging.warn("couldn't find self: %s", e)
            return
        try:
            ballPos = self.world.getBall().pos # are we there yet?
        except Exception, e:
            logging.warn("couldn't find ball: %s", e)
            return

        #print self.me.pos, ballPos
        if self.me.pos[0] == 0 or ballPos[0] == 0:
            self.stop()
            print "POS 0"
            return

        if self.canKick(ballPos):
            self.kick()

    def canKick(self, target_pos):
        if dist(self.me.pos, target_pos) < 20:
            return True

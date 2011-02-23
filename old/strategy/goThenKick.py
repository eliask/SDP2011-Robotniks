from communication.interface import *
from common.utils import *
from common.world import *
from math import *
from strategy import *
import logging

class GoThenKick(Strategy):

    moving = False
    std = False

    def run(self):
        "Run strategy off of the current state of the World."

        #ballPos=np.array(300,200)
        try:
            self.me = self.world.getSelf() # Find out where I am
        except:
            print "couldn't find self"
            return
        try:
            ballPos = self.world.getBall().pos # are we there yet?
        except Exception, e:
            print "couldn't find ball:",e
            raise
            return

        if not self.std:
            self.reset()
            self.std = True
            return

        if self.moveTo( ballPos ): # are we there yet?
            self.kick()

    def moveTo(self, dest):
        logging.debug("moveTo(%s)", pos2string(dest))

        #_dist = dist(dest, self.me.pos)
        _dist = dest[0] - self.me.pos[0]
        logging.debug("Distance to ball: %.3f" % _dist)
        epsilon = 30
        # TODO: implement the canKick predicate instead
        if _dist < epsilon:
            self.stop()
            return True
        else:
            #self.reset()
            if not self.moving:
                self.drive()
                self.moving = True
            return False

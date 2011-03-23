import logging
from utils import pos2string, entCenter, dist
from desp import DESP
import numpy as np

class BallEstimator(object):

    def __init__(self):
        self.Vs = DESP(0.4)
        self.Ps = DESP(0.7)
        self.velocity = np.array([0.,0.])

    def getPos(self, T=0):
        return self.Ps.predict(T)

    def getVelocity(self):
        return self.velocity

    def update(self, balls, dt):
        logging.debug( 'Predicted ball position: %s',
                       pos2string(self.getPos()) )

        pos = self.getPos()
        if len(balls) > 0:
            def ball_dist(x):
                return dist( self.getPos(), entCenter(x) )

            balls_sorted = sorted( balls, key=ball_dist )
            best_match = balls_sorted[0]
            pos = entCenter(best_match)

        self.Ps.update(pos)
        self.Vs.update(pos)

        self.velocity = self.Vs.predict(1./dt) - pos

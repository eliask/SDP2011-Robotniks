import logging
from utils import pos2string, entCenter, dist
from desp import DESP
import numpy as np
from math import cos, sin, atan2

class RobotEstimator(object):

    def __init__(self):
        self.Ps = DESP(0.4)
        self.Vs = DESP(0.5)

        self.orientation = np.array([0.,0.])
        self.velocity    = np.array([0.,0.])

    def getOrientation(self):
        X,Y = self.orientation
        return atan2(Y,X)

    def getPos(self, T=0):
        return self.Ps.predict(T)

    def getVelocity(self):
        return self.velocity

    def update(self, robots, dt):
        logging.debug( 'Predicted robot position: %s',
                       pos2string(self.getPos()) )

        pos = self.getPos()
        if len(robots) > 0 and robots[0] is not None:
            def robot_dist(x):
                return dist( self.getPos(), entCenter(x) )

            robots_sorted = sorted( robots, key=robot_dist )
            best_match = robots_sorted[0]
            pos = entCenter(best_match)
            if 'orient' in best_match:
                angle = best_match['orient']
                self.orientation[:] = cos(angle), sin(angle)

        self.Ps.update(pos)
        self.Vs.update(pos)
        self.velocity = self.Vs.predict(1./dt) - pos

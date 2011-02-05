import logging
from utils import *
from kalman import *

class BallEstimator(Kalman):

    transitionM = [ [ 1, 0, D, 0, 0, 0 ], # p_x
                    [ 0, 1, 0, D, 0, 0 ], # p_y
                    [ 0, 0, 1, 0, D, 0 ], # v_x
                    [ 0, 0, 0, 1, 0, D ], # v_y
                    [ 0, 0, 0, 0, 0, 0 ], # a_x
                    [ 0, 0, 0, 0, 0, 0 ], # a_y
                    ]

    def __init__(self):
        Kalman.__init__(self, 6,2,0, self.transitionM)

    def getPos(self):
        return map(float, (self.prediction[0], self.prediction[1]))

    def getVelocity(self):
        return map(float, (self.prediction[2], self.prediction[3]))

    def update(self, balls, dt):
        #print self.getPos()
        self.predict(dt)
        logging.debug( 'Predicted ball position: %s',
                       pos2string(self.getPos()) )

        if len(balls) == 0:
            self.measurement = self.prediction[:2]
        else:
            def ball_dist(x):
                return dist( self.getPos(), entCenter(x) )

            balls_sorted = sorted( balls, key=ball_dist )
            best_match = balls_sorted[0]
            pos = entCenter(best_match)

            self.measurement[0] = pos[0]
            self.measurement[1] = pos[1]

        self.correct(self.measurement)

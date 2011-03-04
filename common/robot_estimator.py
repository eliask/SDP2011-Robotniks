import logging
from utils import *
from kalman import *

class RobotEstimator(Kalman):
    # p_x, p_y, v_x, v_y, orient, motor dir
    transitionM = [ [ 1, 0, 0, 0, 0, 0 ], # bearing (X component)
                    [ 0, 1, 0, 0, 0, 0 ], # bearing (Y component)
                    [ 0, 0, 1, 0, D, 0 ], # p_x
                    [ 0, 0, 0, 1, 0, D ], # p_y
                    [ 0, 0, 0, 0, 1, 0 ], # v_x
                    [ 0, 0, 0, 0, 0, 1 ], # v_y
                    ]

    def __init__(self):
        # We measure: p_x, p_y, orientation
        # ( We control: motor direction, etc. )
        Kalman.__init__(self, 6,4,0, self.transitionM)

    def getOrientation(self):
        X,Y = map(float, self.measurement[0:2])
        return atan2(Y,X)

    def getPos(self):
        #return tuple( map(float, self.measurement[2:4]) )
        return tuple( map(float, self.prediction[2:4]) )

    def getVelocity(self):
        return tuple( map(float, self.prediction[4:6]) )

    def update(self, robots, dt):
        self.predict(dt)
        logging.debug( 'Predicted robot position: %s',
                       pos2string(self.getPos()) )

        if len(robots) == 0 or robots[0] is None:
            self.measurement = self.prediction[:4]
        else:
            def robot_dist(x):
                return dist( self.getPos(), entCenter(x) )

            robots_sorted = sorted( robots, key=robot_dist )
            best_match = robots_sorted[0]
            pos = entCenter(best_match)
            self.measurement[2] = pos[0]
            self.measurement[3] = pos[1]
            if 'orient' in best_match:
                angle = best_match['orient']
                self.measurement[0] = cos(angle)
                self.measurement[1] = sin(angle)

        self.correct(self.measurement)

import logging
from utils import *
from kalman import Kalman

class RobotEstimator(Kalman):
    """TODO: also track
    - Max. speed (1)
    - Max. angular velocity (1)
    - Max kicker launch speed (1)
    """

    # p_x, p_y, v_x, v_y, a_x, a_y, orient, motor dir
    transitionM = [ [ 1, 0, 1, 0, 0, 0, 0, 0], # p_x
                    [ 0, 1, 0, 1, 0, 0, 0, 0], # p_y
                    [ 0, 0, 1, 0, 1, 0, 0, 0], # v_x
                    [ 0, 0, 0, 1, 0, 1, 0, 0], # v_y
                    [ 0, 0, 0, 0, 1, 0, 0, 0], # a_x
                    [ 0, 0, 0, 0, 0, 1, 0, 0], # a_y
                    [ 0, 0, 0, 0, 0, 0, 1, 1], # orientation
                    [ 0, 0, 0, 0, 0, 0, 0, 1], # angular velocity (delta ^)
                    ]

    def __init__(self):
        # We measure: p_x, p_y, orientation
        # ( We control: motor direction, etc. )
        Kalman.__init__(self, 8,3,0, self.transitionM)

    def getPos(self):
        return map(float, (self.prediction[0], self.prediction[1]))

    def getVelocity(self):
        return map(float, (self.prediction[2], self.prediction[3]))

    def getOrientation(self):
        return float(self.prediction[6])

    def update(self, robots):
        self.predict()
        logging.debug( 'Predicted robot position: %s',
                       pos2string(self.getPos()) )

        if len(robots) == 0 or robots[0] is None:
            self.measurement = self.prediction[:3]
        else:
            def robot_dist(x):
                return dist( self.getPos(), entCenter(x) )

            robots_sorted = sorted( robots, key=robot_dist )
            best_match = robots_sorted[0]
            pos = entCenter(best_match)

            self.measurement[0] = pos[0]
            self.measurement[1] = pos[1]
            self.measurement[2] = best_match['orient']

        self.correct(self.measurement)
        self.predict()

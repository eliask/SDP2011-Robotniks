import cv
import logging
from utils import *

class RobotEstimator(object):
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

        self.kalman = cv.CreateKalman( 8, 3, 0 )

        # Couldn't find a more elegant working way to do this
        for i in range(len(self.transitionM)):
            for j in range(len(self.transitionM)):
                self.kalman.transition_matrix[i,j] = self.transitionM[i][j]

        self.measurement = cv.CreateMat( 3, 1, cv.CV_32FC1 )
        cv.Zero(self.measurement)

        cv.SetIdentity( self.kalman.measurement_matrix, 1 )
        cv.SetIdentity( self.kalman.process_noise_cov, 1e-5 )
        cv.SetIdentity( self.kalman.measurement_noise_cov, 1e-1 )
        cv.SetIdentity( self.kalman.error_cov_post, 1 )
        cv.Zero( self.kalman.state_post )

    def getPos(self):
        return cvmat2list(self.prediction)[:2]

    def getVelocity(self):
        return cvmat2list(self.prediction)[2:4]

    def getOrientation(self):
        return cvmat2list(self.prediction)[6]

    def update(self, robots):
        prediction = cv.KalmanPredict( self.kalman )[:,0]
        predicted_pos = cvmat2list(prediction)[:2]
        logging.debug( 'Predicted robot position: %s',
                       pos2string(predicted_pos) )

        if len(robots) == 0 or robots[0] is None:
            self.measurement = prediction[:3,:]
        else:
            def robot_dist(x):
                return dist( predicted_pos, entCenter(x) )

            robots_sorted = sorted( robots, key=robot_dist )
            print robots_sorted
            best_match = robots_sorted[0]
            self.measurement[:2,0] = entCenter(best_match)
            self.measurement[2,0] = best_match['orient']

        cv.KalmanCorrect( self.kalman, self.measurement )

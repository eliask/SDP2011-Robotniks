import cv
import logging
from utils import *

class BallEstimator(object):
    #              p_x, p_y, v_x, v_y, a_x, a_y
    transitionM = [ [ 1, 0, 1, 0, 0, 0 ], # p_x
                    [ 0, 1, 0, 1, 0, 0 ], # p_y
                    [ 0, 0, 1, 0, 1, 0 ], # v_x
                    [ 0, 0, 0, 1, 0, 1 ], # v_y
                    [ 0, 0, 0, 0, 1, 0 ], # a_x
                    [ 0, 0, 0, 0, 0, 1 ], # a_y
                    ]

    def __init__(self):
        self.kalman = cv.CreateKalman( 6, 2, 0 )

        # Couldn't find a more elegant working way to do this
        for i in range(len(self.transitionM)):
            for j in range(len(self.transitionM)):
                self.kalman.transition_matrix[i,j] = self.transitionM[i][j]

        self.measurement = cv.CreateMat( 2, 1, cv.CV_32FC1 )
        cv.Zero(self.measurement)

        cv.SetIdentity( self.kalman.measurement_matrix, 1 )
        cv.SetIdentity( self.kalman.process_noise_cov, 1e-1 )
        cv.SetIdentity( self.kalman.measurement_noise_cov, 1e-2 )
        cv.SetIdentity( self.kalman.error_cov_post, 1 )
        cv.Zero( self.kalman.state_post )
        self.prediction = cv.KalmanPredict( self.kalman )[:,0]

    def getPos(self):
        return cvmat2list(self.prediction)[:2]

    def getVelocity(self):
        return cvmat2list(self.prediction)[2:4]

    def update(self, balls):
        logging.debug('Updating ball Kalman filter')
        prediction = cv.KalmanPredict( self.kalman )[:,0]
        predicted_pos = cvmat2list(prediction)[:2]
        logging.debug( 'Predicted ball position: %s',
                       pos2string(predicted_pos) )

        if len(balls) == 0:
            self.measurement = prediction[:2]
        else:
            def ball_dist(x):
                return dist( predicted_pos, entCenter(x) )

            balls_sorted = sorted( balls, key=ball_dist )
            print balls_sorted
            best_match = balls_sorted[0]
            pos = entCenter(best_match)

            print pos
            self.measurement[0,0] = pos[0]
            self.measurement[1,0] = pos[1]

        cv.KalmanCorrect( self.kalman, self.measurement )
        self.prediction = cv.KalmanPredict( self.kalman )[:,0]

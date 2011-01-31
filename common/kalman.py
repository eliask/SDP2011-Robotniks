import numpy as np

class Kalman:
    #TODO: test numerical stability over a long test run

    def __init__(self, state, measure, control, transitionMatrix):
        self.measure = measure
        self.state = state
        self.control = control

        # Measurement matrix:
        self.H = np.mat( np.eye(measure, state) )
        # Measurement noise covariance:
        self.R = np.mat( np.eye(measure, measure) ) * 1e-2
        # Process noise covariance
        self.Q = np.mat( np.eye(state, state) ) * 1e-1
        # State vector estimate covariance
        self.P = np.mat( np.eye(state, state) )

        # Control covariance (not needed atm)
        # B = np.mat( np.eye(control, state) )

        self.F = np.mat( transitionMatrix )
        self.x = np.mat( np.zeros((state, 1)) )

        self.measurement = np.mat( np.zeros((measure, 1)) )
        self.prediction = self.predict()

    def predict(self):
        #  Prediction for state vector and covariance:
        self.x = self.F * self.x # + B*u
        self.P = self.F * self.P * np.transpose(self.F) + self.Q
        return self.x

    def correct(self, measurement):
        z = measurement

        # Compute Kalman gain factor:
        try:
            K = self.P * np.transpose(self.H) * \
                np.linalg.inv(self.H * self.P * \
                                  np.transpose(self.H) + self.R)
        except np.linalg.linalg.LinAlgError:
            # TODO: is this correct enough?
            K = np.zeros((self.state, self.measure))

        # Correct based on measurement:
        self.x = self.x + K*(z - self.H * self.x)
        self.P = (1 - K * self.H) * self.P

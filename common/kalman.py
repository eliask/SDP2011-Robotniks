import numpy as np

D = 1e1000 #=inf; used to signal which bits are dt
class Kalman:

    def __init__(self, state, measure, control, transitionMatrix):
        self.measure = measure
        self.state = state
        self.control = control

        # Measurement matrix:
        self.H = np.mat( np.eye(measure, state) )
        # Measurement noise covariance:
        self.R = np.mat( np.eye(measure, measure) ) * 20
        # Process noise covariance
        self.Q = np.mat( np.eye(state, state) ) * 3
        # State vector estimate covariance
        self.P = np.mat( np.eye(state, state) )

        # Control covariance (not needed atm)
        # B = np.mat( np.eye(control, state) )

        self.F = np.mat( transitionMatrix )
        self.x = np.mat( np.zeros((state, 1)) )

        self.measurement = np.mat( np.zeros((measure, 1)) )
        self.predict(1)

    def predict(self, dt):
        inf = 1e1000
        F = np.mat(np.zeros( (self.state, self.state) ))
        for i in range(F.shape[0]):
            for j in range(F.shape[1]):
                if self.F[i,j] == D:
                    F[i,j] = dt
                else:
                    F[i,j] = self.F[i,j]

        #  Prediction for state vector and covariance:
        self.x_est = F * self.x # + B*u
        self.P_est = F * self.P * np.transpose(F) + self.Q
        self.prediction = self.x_est

    def correct(self, measurement):
        z = measurement

        x_error = measurement - self.H * self.x_est
        P_error = self.H * self.P * np.transpose(self.H) + self.R
        try:
            K = self.P_est * np.transpose(self.H) * np.linalg.inv(P_error)
        except np.linalg.linalg.LinAlgError, e:
            # Should not happen, but we probably don't want a system crash either
            logging.error("Error with matrix inversion: %s", e)
            K = np.ones((self.state, self.measure))

        self.x = self.x_est + K * x_error

        # Correct based on measurement:
        self.P = (np.eye(self.state) - K * self.H) * self.P_est

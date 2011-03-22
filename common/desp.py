import numpy as np

class DESP(object):
    """Double exponential smoothing-based prediction

    Joseph J. LaViola. 2003. Double exponential smoothing: an
    alternative to Kalman filter-based predictive tracking. In
    Proceedings of the workshop on Virtual environments 2003 (EGVE
    '03). ACM, New York, NY, USA, 199-206. DOI=10.1145/769953.769976
    http://doi.acm.org/10.1145/769953.769976
    """

    def __init__(self, alpha, len=2):
        self.alpha = alpha
        self.S1_prev = np.array([0]*len)
        self.S2_prev = np.array([0]*len)
        self.S1 = np.array([0]*len)
        self.S2 = np.array([0]*len)

    def update(self, vector):
        A = self.alpha
        self.S1 = A*vector  + (1-A)*self.S1_prev
        self.S2 = A*self.S1 + (1-A)*self.S2_prev
        self.S1_prev, self.S2_prev = self.S1, self.S2

    def predict(self, time):
        T = time
        A = self.alpha
        prediction = (2 + A*T/(1-A))*self.S1 - (1 + A*T/(1-A))*self.S2
        return prediction

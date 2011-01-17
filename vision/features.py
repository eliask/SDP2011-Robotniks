from opencv import cv, highgui
from utils import *
import threshold

# _red = cv.cvScalar(0, 0, 255, 0);
# _green = cv.cvScalar(0, 255, 0, 0);

def detect_ball(self, frame):
    thresholded = threshold.ball(frame)
    candidates = self.find_connected_components(thresholded)
    centers = map(lambda x:x[0], candidates)
    tuples = map(BoxCenterPos, centers)
    return tuples
    # cv.cvHoughCircles(gray, circles, CV_HOUGH_GRADIENT,
    #                   2, gray->rows/4, 200, 100)

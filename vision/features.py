from opencv import cv, highgui
from utils import *
import threshold

params = [30,50]

def detect_ball(self, frame):
    thresholded = threshold.ball(frame)
    candidates = self.find_connected_components(thresholded)
    centers = map(lambda x:x[0], candidates)
    tuples = map(BoxCenterPos, centers)
    return tuples

def detect_dirmarker(rect):
    pass

def detect_circles(rect):
    """Detect circles in the picture

    the Hough circle transform parameters min_radius and max_radius
    are adjusted as follows:

    * The black direction marker is around 8 to 11 pixels wide.
    * The ball is around 12 and 16 pixels wide.

    The above estimates are taken with GIMP. The lower bounds are
    obtained using the darker, inner pixels and the upper bounds using
    the lighter edge pixels. Since the Hough circle transform is
    resistant against damage (it could work with only half of the
    circle present), we stick with radii obtained from these measures
    and not try to "account for" the cases where the circles are
    somehow obscured and look smaller to the eye.
    """
    out = cv.cvCloneImage(rect)
    cv.cvSmooth(rect, rect, cv.CV_GAUSSIAN, 9, 9)
    size = cv.cvGetSize(rect)
    gray = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
    cv.cvCvtColor(rect, gray, cv.CV_BGR2GRAY)
    storage = cv.cvCreateMemStorage(0)

    print "PARAMS:", params

    #Note: circles.total denotes the number of circles
    circles = cv.cvHoughCircles(gray, storage, cv.CV_HOUGH_GRADIENT,
                                2, #dp / resolution
                                10, #circle dist threshold
                                1+params[0], #param1
                                1+params[1], #param2
                                # 2,  #min_radius
                                # 12,  #max_radius
                                )

    for circle in circles:
        # It took a fair amount of trouble to find out how to do this properly!
        x, y, radius = [circle[i] for i in range(3)]

        cv.cvCircle(rect, Point(x, y), cv.cvRound(min(30,radius)), cv.CV_RGB(300,1,1))

    return rect


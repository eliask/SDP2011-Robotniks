from opencv import cv, highgui
from utils import *
import threshold
import segmentation

class FeatureExtraction:

    # Sizes of various features
    # Format : ( min_w, max_w, min_h, max_H)
    # width is defined as the longer dimension
    Sizes = { 'balls'     : (3,  25,  3, 25),
              'T'         : (35, 55, 25, 35),
              'robots'    : (50, 80, 35, 60),
              'dirmarker' : (3,  12, 3,  12),
            }

    def __init__(self, size):
        self.gray = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)

    def __del__(self):
        cv.cvReleaseImage(self.gray)

    def features(self, Iobjects):
        """Extract relevant features from objects
        :: CvMat -> dict( label -> [ dict() ] )

        Returns a dictionary containing the positions of robots and ball.
        Both types contain 'box' and 'rect', which refer to their
        bounding boxes and their bounding rectangles, respectively.

        Performs size-checking on all entities but doesn't eliminate
        all multiplicity.
        """
        cv.cvCvtColor(Iobjects, self.gray, cv.CV_BGR2GRAY)
        objects = self.segment(self.gray)

        ents = {}
        ents['robots'] = [ obj for obj in objects if self.sizeMatch(obj, 'robots') ]
        self.detectBall(Iobjects, ents)
        self.detectRobots(Iobjects, ents)

        return ents

    def detectBall(self, frame, ents):
        ents['balls'] = []
        for ball_cand in self.segment(threshold.ball(frame)):
            R = ball_cand['rect']
            if self.sizeMatch(ball_cand, 'balls'):
                ents['balls'].append(ball_cand)

    def detectRobots(self, frame, ents):
        "Detect the potential robots in the image"
        yellow = blue = None
        neither = []
        for robot_cand in ents['robots']:
            R = robot_cand['rect']
            sub = cv.cvGetSubRect(frame, (R.x, R.y, R.width, R.height))
            #print (R.x, R.y, R.width, R.height)

            robot_cand['dirmarker'] = self.detectDirMarker(sub)

            robot_cand['side'] = None
            robot_cand['T'] = self.detectYellow(sub)
            if robot_cand['T']:
                yellow = robot_cand
                robot_cand['side'] = 'yellow'
            else:
                robot_cand['T'] = self.detectBlue(sub)
                if robot_cand['T']:
                    blue = robot_cand
                    robot_cand['side'] = 'blue'
                else:
                    neither.append(robot_cand)

        self.eliminateRobots(ents, blue, yellow, neither)
        self.assignPlayers(ents)

    def assignPlayers(self, ents):
        "Create the entities 'blue' and 'yellow'"
        ents['blue'] = ents['yellow'] = None
        for robot in ents['robots']:
            if robot['side'] == 'blue':
                ents['blue'] = robot
            elif robot['side'] == 'yellow':
                ents['yellow'] = robot

    def eliminateRobots(self, ents, blue, yellow, neither):
        """Use logic to eliminate unnecessary robot candidates

        We assume there must be two robots around at all times and
        that we won't be dealing with any additional objects.
        """
        if blue and yellow:
            ents['robots'] = [blue, yellow]
        elif len(ents['robots']) == 2:
            if yellow and not blue:
                neither[0]['side'] = 'blue'
            elif blue and not yellow:
                neither[0]['side'] = 'yellow'

    def detectYellow(self, sub):
        yellow = self.segment(threshold.yellowTAndBall(sub))
        for Y in yellow:
            #print "Y:", Y['box'].size.width, Y['box'].size.height
            if self.sizeMatch(Y, 'T'):
                return Y
        return None

    def detectBlue(self, sub):
        blue = self.segment(threshold.blueT(sub))
        for B in blue:
            #print "B:", B['box'].size.width, B['box'].size.height
            if self.sizeMatch(B, 'T'):
                return B
        return None

    def detectDirMarker(self, sub):
        dirmarker = None
        dirs = self.segment(threshold.dirmarker(sub))
        for d in dirs:
            if self.sizeMatch(d, 'dirmarker'):
                dirmarker = d
        return dirmarker

    def segment(self, thresholded):
        return segmentation.find_connected_components(thresholded)

    def sizeMatch(self, obj, name):
        width, height = self.getSize(obj)
        if  self.Sizes[name][0] < width  < self.Sizes[name][1] \
        and self.Sizes[name][2] < height < self.Sizes[name][3]:
            return True
        else:
            return False

    def getSize(self, obj):
        box = obj['box']
        width = max(box.size.width, box.size.height)
        height = min(box.size.width, box.size.height)
        return width, height

    hough_params = [30,50]
    def detectCircles(self, rect):
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
        cv.cvCvtColor(rect, gray, cv.CV_BGR2GRAY)
        storage = cv.cvCreateMemStorage(0)

        print "PARAMS:", params

        #Note: circles.total denotes the number of circles
        circles = cv.cvHoughCircles(self.gray, storage, cv.CV_HOUGH_GRADIENT,
                                    2, #dp / resolution
                                    10, #circle dist threshold
                                    1+self.hough_params[0], #param1
                                    1+self.hough_params[1], #param2
                                    # 2,  #min_radius
                                    # 12,  #max_radius
                                    )

        for circle in circles:
            # It took a fair amount of trouble to find out how to do this properly!
            x, y, radius = [circle[i] for i in range(3)]

            cv.cvCircle(rect, Point(x, y), cv.cvRound(min(30,radius)), cv.CV_RGB(300,1,1))

        return rect


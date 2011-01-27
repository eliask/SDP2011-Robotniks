import cv
from .common.utils import *
import threshold
import segmentation
import logging

class FeatureExtraction:

    # Sizes of various features
    # Format : ( min_w, max_w, min_h, max_H)
    # width is defined as the longer dimension
    Sizes = { 'balls'     : (3,  25,  3, 25),
              'T'         : (15, 35, 10, 25),
              'robots'    : (38, 80, 20, 60),
              'dirmarker' : (5,  12, 5,  12),
            }

    def __init__(self, size):
        self.gray16 = cv.CreateImage(size, cv.IPL_DEPTH_16S, 1)
        self.gray8 = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
        self.Itmp = cv.CreateImage(size, cv.IPL_DEPTH_8U, 3)

    def features(self, Iobjects, threshold):
        """Extract relevant features from objects
        :: CvMat -> CvMat -> dict( label -> [ dict() ] )

        Returns a dictionary containing the positions of robots and ball.
        Both types contain 'box' and 'rect', which refer to their
        bounding boxes and their bounding rectangles, respectively.

        Performs size-checking on all entities but doesn't eliminate
        all multiplicity.
        """
        self.threshold = threshold

        assert Iobjects.nChannels == 3, "features must take BGR input"
        assert imSize(Iobjects) == imSize(self.gray8), \
            ("Sizes don't match!", size1, size2)

        cv.CvtColor(Iobjects, self.gray8, cv.CV_BGR2GRAY)

        logging.info("Segmenting the image for objects")
        objects = self.segment(self.gray8)

        ents = {}
        ents['robots'] = [ obj for obj in objects
                           if self.sizeMatch(obj, 'robots') ]

        logging.debug("Detecting ball in the image")
        self.detectBall(Iobjects, ents)
        logging.info("Found %d balls." % len(ents['balls']))

        logging.debug("Detecting robots in the image")
        self.detectRobots(Iobjects, ents)
        logging.info("Found %d robots." % len(ents['robots']))

        for colour in ('blue', 'yellow'):
            if ents[colour]:
                logging.debug("Found a %s robot" % colour)
            else:
                logging.warn("Could not find a %s robot!" % colour)

        return ents

    def segment(self, thresholded):
        return segmentation.find_connected_components(thresholded)

    def detectBall(self, frame, ents):
        ents['balls'] = []
        for ball_cand in self.segment(self.threshold.ball(frame)):
            R = ball_cand['rect']
            if self.sizeMatch(ball_cand, 'balls'):
                ents['balls'].append(ball_cand)

    def detectRobots(self, frame, ents):
        "Detect the potential robots in the image"
        yellow = blue = None
        neither = []
        for ent in ents['robots']:
            cv.SetImageROI(frame, ent['rect'])

            ent['dirmarker'] = self.detectDirMarker(ent, frame)

            ent['side'] = None
            ent['T'] = self.detectYellow(frame)
            if ent['T']:
                yellow = ent
                ent['side'] = 'yellow'
            else:
                ent['T'] = self.detectBlue(frame)
                if ent['T']:
                    blue = ent
                    ent['side'] = 'blue'
                else:
                    logging.info( "Robot-size object of size %s at %s"
                                  "does not have a T marker",
                                  *entDimPos(ent) )
                    neither.append(ent)

        # TODO: Reconstruct robots based on recognised Ts.
        # This is a realistic scenario as varying lighting
        # levels can make the body invisible after thresholding

        #self.eliminateRobots(ents, blue, yellow, neither)
        cv.ResetImageROI(frame)
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
        elif len(ents['robots']) == 2 and len(neither) > 0:
            if yellow and not blue:
                neither[0]['side'] = 'blue'
            elif blue and not yellow:
                neither[0]['side'] = 'yellow'

    def detectYellow(self, sub):
        yellow = self.segment(self.threshold.yellowT(sub))
        for Y in yellow:
            if self.sizeMatch(Y, 'T'):
                logging.info( "found a yellow T of size %s at %s",
                              *entDimPos(Y) )
                return Y
        return None

    def detectBlue(self, sub):
        blue = self.segment(self.threshold.blueT(sub))
        for B in blue:
            if self.sizeMatch(B, 'T'):
                logging.debug( "found a blue T of size %s at %s",
                               *entDimPos(B) )
                return B
        return None

    def detectDirMarker(self, robot, sub):
        dirs = self.segment(self.threshold.dirmarker(sub))
        for D in dirs:
            if self.sizeMatch(D, 'dirmarker') and inBox(robot, D):
                logging.debug( "found a direction marker of size %s at %s",
                               *entDimPos(D) )
                return D
        return None

    def sizeMatch(self, obj, name):
        width, height = entSize(obj)

        assert self.Sizes[name][0] <= self.Sizes[name][1] and \
            self.Sizes[name][2] <= self.Sizes[name][3], \
            ("Invalid Size entry for", name, self.Sizes[name])

        return self.Sizes[name][0] < width  < self.Sizes[name][1] \
            and self.Sizes[name][2] < height < self.Sizes[name][3]

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
        out = cv.CloneImage(rect)
        cv.Smooth(rect, rect, cv.CV_GAUSSIAN, 9, 9)
        size = cv.GetSize(rect)
        cv.CvtColor(rect, gray, cv.CV_BGR2GRAY)
        storage = cv.CreateMemStorage(0)

        print "PARAMS:", params

        #Note: circles.total denotes the number of circles
        circles = cv.HoughCircles(self.gray, storage, cv.CV_HOUGH_GRADIENT,
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

            cv.Circle(rect, Point(x, y), cv.Round(min(30,radius)), cv.CV_RGB(300,1,1))

        return rect


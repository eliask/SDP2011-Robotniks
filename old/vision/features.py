import cv
from common.utils import *
import threshold
import segmentation
import logging

class FeatureExtraction:

    # Sizes of various features
    # Format : ( min_w, max_w, min_h, max_H)
    # width is defined as the longer dimension
    Sizes = { 'balls'     : (3,  25,  3, 25),
              #'T'         : (15, 35, 10, 25),
              'T'         : (5, 45, 3, 40),
              'robots'    : (28, 80, 20, 60),
              'dirmarker' : (5,  12, 5,  12),
            }

    def __init__(self, size, threshold=None):
        self.gray16 = cv.CreateImage(size, cv.IPL_DEPTH_16S, 1)
        self.gray8 = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
        self.Itmp = cv.CreateImage(size, cv.IPL_DEPTH_8U, 3)
        self.threshold = threshold

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
        logging.info("Found %d balls.", len(ents['balls']))

        logging.debug("Detecting robots in the image")
        self.detectRobots(Iobjects, ents)
        logging.info("Found %d robots.", len(ents['robots']))

        for colour in ('blue', 'yellow'):
            if ents[colour]:
                logging.debug("Found a %s robot", colour)
            else:
                #self.detect_robot_from_T(Iobjects, ents, colour)
                logging.info("Could not find a %s robot!", colour)
                pass

        return ents

    def segment(self, thresholded):
        return segmentation.find_connected_components(thresholded)

    def detectBall(self, frame, ents):
        ents['balls'] = []
        for ball_cand in self.segment(self.threshold.ball(frame)):
            R = ball_cand['rect']
            if self.sizeMatch(ball_cand, 'balls'):
                ents['balls'].append(ball_cand)

    def detect_robot_from_T(self, frame, ents, colour):
        if colour == 'yellow':
            ent_T = self.detectYellow(frame)
        else:
            ent_T = self.detectBlue(frame)

        if ent_T:
            ents[colour] = ent_T
            ents[colour]['T'] = ent_T
            ents[colour]['dirmarker'] = None

    def detectRobots(self, frame, ents):
        "Detect the potential robots in the image"
        yellow = blue = None
        neither = []
        for ent in ents['robots']:
            cv.SetImageROI(frame, ent['rect'])

            ent['dirmarker'] = self.detectDirMarker(ent, frame)

            ent['side'] = None
            ent['T'], img = self.detectYellow(frame)
            if ent['T']:
                yellow = ent
                ent['side'] = 'yellow'
            else:
                ent['T'], img = self.detectBlue(frame)
                if ent['T']:
                    blue = ent
                    ent['side'] = 'blue'
                else:
                    logging.info( "Robot-size object of size %s at %s"
                                  "does not have a T marker",
                                  *entDimPos(ent) )
                    neither.append(ent)

            self.convertRobotCoordinates(ent)
            # cv.ShowImage("R"+str(ent['side']), frame)
            if ent['T']:
                center = tuple(-entCenter(ent) + entCenter(ent['T']))
                print "robot:",center
                radius = 10
                if img:
                    circle = cv.Circle(img, center, radius, (0,0,0,0), -1)
                    cv.ShowImage(ent['side'], img)

        # TODO: Reconstruct robots based on recognised Ts.
        # This is a realistic scenario as varying lighting
        # levels can make the body invisible after thresholding

        #self.eliminateRobots(ents, blue, yellow, neither)
        cv.ResetImageROI(frame)
        self.assignPlayers(ents)

    def convertRobotCoordinates(self, robot):
        if robot['T']:
            self.convertCoordinates(robot, robot['T'])
        if robot['dirmarker']:
            self.convertCoordinates(robot, robot['dirmarker'])

    def convertCoordinates(self, ent, sub):
        "Convert relative coordinates to absolute"
        # The sub-entity's bounding rectangle's coordinates are
        # relative to the parent entity.
        w,h = entRect(sub)[2:]
        sub['rect'] = list( entRect(ent)[:2] + entRect(sub)[:2] )

        sub['rect'] += [w,h]
        sub['box'] = ( entCenter(ent) + entCenter(sub),
                       entDim(sub), entAngle(sub) )

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
        img = self.threshold.yellowT(sub)
        yellow = self.segment(cv.CloneImage(img))
        moments = cv.Moments(img, 1)
        asd = cv.GetCentralMoment(moments, 0,0)
        print "STUFF:",asd
        #yellow = self.segment(self.threshold.yellowT(sub))
        img=None

        for Y in yellow:
            if self.sizeMatch(Y, 'T'):
                logging.info( "found a yellow T of size %s at %s",
                              *entDimPos(Y) )
                return Y, img
        return None, None

    def detectBlue(self, sub):
        #img = self.threshold.blueT(sub)
        # blue = self.segment(cv.CloneImage(img))
        blue = self.segment(self.threshold.blueT(sub))
        img=None

        for B in blue:
            if self.sizeMatch(B, 'T'):
                logging.debug( "found a blue T of size %s at %s",
                               *entDimPos(B) )
                return B, img
        return None, None

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

    #hough_params = [30,50]
    hough_params = [180,120]
    def detectCircles(self, rect):
        """Detect circles in the picture

        the Hough circle transform parameters min_radius and max_radius
        are adjusted as follows (for the 768x576 image):

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
        cv.CvtColor(rect, self.gray8, cv.CV_BGR2GRAY)
        #storage = cv.CreateMemStorage(0)
        storage = cv.CreateMat(7000, 1, cv.CV_32FC3)

        print "PARAMS:", self.hough_params

        #Note: circles.total denotes the number of circles
        circles = cv.HoughCircles(self.gray8, storage, cv.CV_HOUGH_GRADIENT,
                                    3, #dp / resolution
                                    2, #circle dist threshold
                                    max(1,self.hough_params[0]), #param1
                                    max(1,self.hough_params[1]), #param2
                                    2,  #min_radius
                                    14,  #max_radius
                                    )

        for x,y,radius in [storage[i,0] for i in range(storage.rows)]:
            cv.Circle(rect, (x,y), cv.Round(radius), cv.CV_RGB(300,1,1))
        cv.ShowImage("BASD", rect)

        return rect


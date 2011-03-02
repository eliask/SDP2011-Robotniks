from common.utils import *
import cv, logging
import segmentation, threshold

class FeatureExtraction:

    # Sizes of various features
    # Format : ( min_w, max_w, min_h, max_H)
    # width is defined as the longer dimension
    Sizes = { 'balls'     : (4,  20,  4, 20),
              'T'         : (20, 55, 15, 40),
              'dirmarker' : (3,  12, 3,  12),
            }

    def __init__(self, size, threshold=None):
        self.gray8 = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
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
        size1 = (Iobjects.width, Iobjects.height)
        size2 = (self.gray8.width, self.gray8.height)
        assert imSize(Iobjects) == imSize(self.gray8), \
            ("Sizes don't match!", size1, size2)

        cv.CvtColor(Iobjects, self.gray8, cv.CV_BGR2GRAY)

        logging.info("Segmenting the image for objects")
        objects = self.segment(self.gray8)

        ents = {'balls':[], 'robots':[]}

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
                logging.info("Could not find a %s robot!", colour)

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
        ents['yellow'] = [x for x in self.detectYellow(frame)]
        ents['blue'] = [x for x in self.detectBlue(frame)]
        for robot in ents['yellow']:
            self.getOrientation(frame, robot, 'yellow', self.threshold.yellowT)
        for robot in ents['blue']:
            self.getOrientation(frame, robot, 'blue', self.threshold.blueT)

        ents['robots'].extend(ents['yellow'])
        ents['robots'].extend(ents['blue'])

    def detectYellow(self, sub):
        yellow = self.segment(self.threshold.yellowT(sub))
        for Y in yellow:
            if self.sizeMatch(Y, 'T'):
                logging.info( "found a yellow T of size %s at %s",
                              *entDimPos(Y) )
                yield Y

    def detectBlue(self, sub):
        blue = self.segment(self.threshold.blueT(sub))
        for B in blue:
            if self.sizeMatch(B, 'T'):
                logging.debug( "found a blue T of size %s at %s",
                               *entDimPos(B) )
                yield B

    def detectDirMarker(self, robot, sub):
        dirs = self.segment(self.threshold.dirmarker(sub))
        for D in dirs:
            if self.sizeMatch(D, 'dirmarker') and inBox(robot, D):
                logging.debug( "found a direction marker of size %s at %s",
                               *entDimPos(D) )
                yield D

    def sizeMatch(self, obj, name):
        width, height = entSize(obj)

        assert self.Sizes[name][0] <= self.Sizes[name][1] and \
            self.Sizes[name][2] <= self.Sizes[name][3], \
            ("Invalid Size entry for", name, self.Sizes[name])

        return self.Sizes[name][0] < width  < self.Sizes[name][1] \
            and self.Sizes[name][2] < height < self.Sizes[name][3]

    def getOrientation(self, frame, robot, name, thresh):
        cv.SetImageROI(frame, robot['rect'])
        img = thresh(frame)
        cv.ResetImageROI(frame)

        offset = 40
        c = entCenter(robot)
        nhood = ( max(0,c[0] - offset), max(0,c[1] - offset),
                 2*offset, 2*offset )
        cv.SetImageROI(frame, nhood)
        img2 = self.threshold.dirmarker(frame)
        cv.ResetImageROI(frame)

        cv.Dilate(img,img)
        cv.Erode(img,img)
        cv.Erode(img,img)
        cv.Erode(img,img)

        def computeMoment(contour):
            moments = cv.Moments(contour, 1)

            area= cv.GetSpatialMoment(moments,0,0)
            if area == 0: return
            x = cv.GetSpatialMoment(moments,1,0)
            y = cv.GetSpatialMoment(moments,0,1)
            return x,y, area

        def centralMoment(img):
            contours = segmentation.get_contours(img)
            if not contours: return
            all_moments = map(computeMoment, contours)
            all_moments = filter(lambda x:x is not None, all_moments)
            areas = map(lambda x:x[-1], all_moments)
            center = sum( map(lambda x:np.array(x[:-1]), all_moments) )
            area = sum(areas)
            if area == 0: return
            return center / area

        cv.SetImageROI(frame, nhood)
        white = self.threshold.white(frame)
        cv.ResetImageROI(frame)

        Tcenter = centralMoment(img)
        if Tcenter is None: return
        xcT,ycT = Tcenter

        Wcenter = centralMoment(white)
        if Wcenter is None: return
        xcW,ycW = Wcenter

        R = robot['rect']; c = entCenter(robot)
        TgeomCenter = entCenter(robot)
        xT,yT = TgeomCenter
        #xcW,ycW = xcW+R[0], ycW+R[1]
        dx,dy = xT-xcW-nhood[0], yT-ycW-nhood[1]
        robot['orient'] = atan2(dy,dx)

        ### Absolute coords:
        #cv.Circle(frame, tuple(TgeomCenter), 12, (50,50,200), -1)
        # print Wcenter, TgeomCenter, Tcenter
        # print xcW+nhood[0], ycW+nhood[1]

        # cv.SetImageROI(frame, nhood)
        ### Relative coords:
        #cv.Circle(frame, tuple(Tcenter), 12, (200,50,140), -1)
        # cv.Circle(frame, tuple(Wcenter), 12, (150,150,150), -1)
        # cv.ResetImageROI(frame)
        # cv.Circle( frame, (xcW+nhood[0], ycW+nhood[1]), 
        #            8, (255,255,255), -1 )

        return

        circles = self.detectCircles(img2)
        if False and circles:
            x,y,radius = circles[0]
            dx,dy = center[0]-x, center[1]-y
            angle = atan2(dy,dx)
            robot['orient'] = angle
            return

        radius = int(0.8*sqrt((x/area)**2 + (y/area)**2))
        col=(255,255,255)
        col=(0,0,0)
        cv.Circle(img, (x/area, y/area), radius, col, -1)
        objects = self.segment(img)

        if objects:
            robot['T_tip'] = objects[0]
            tip_pos = entCenter(objects[0])
            dy,dx = np.array(tip_pos) - center
            angle = atan2(dy,dx)
            robot['orient'] = angle
            return
 
        C = segmentation.get_contours(img)
        if not C: return

        moments = cv.Moments(C[0], 1)
        #moments = cv.Moments(img, 1)
        y= cv.GetSpatialMoment(moments,0,1)
        x= cv.GetSpatialMoment(moments,1,0)

        area= cv.GetSpatialMoment(moments,0,0)
        if area == 0: return
        center = x/area, y/area
        diff = center[0] - img.width/2.0, center[1] - img.height/2.0

        angle = atan2(2*diff[1], 2*diff[0])
        robot['orient'] = angle


    hough_params = [140,15]
    track=None
    def detectCircles(self, rect, gray=False):
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
        cv.Smooth(rect, rect, cv.CV_GAUSSIAN, 3,3)
        s = self.segment(rect)
        if len(s) == 1:
            C = segmentation.get_contours(rect)
            if not C: return []

            moments = cv.Moments(C[0], 1)
            area= cv.GetSpatialMoment(moments,0,0)

            if area == 0: return []
            y= cv.GetSpatialMoment(moments,0,1) / area
            x= cv.GetSpatialMoment(moments,1,0) / area
            return [(x,y,0)]

        size = cv.GetSize(rect)
        tmp = cv.CloneImage(rect)
        storage = cv.CreateMat(100, 1, cv.CV_32FC3)


        #Note: circles.total denotes the number of circles
        circles = cv.HoughCircles(rect, storage, cv.CV_HOUGH_GRADIENT,
                                  1, 40, 20, 10, 2, 30 )

        out = cv.CreateImage(size, cv.IPL_DEPTH_8U, 3)
        cv.CvtColor(rect, out, cv.CV_GRAY2BGR)

        circles = [storage[i,0] for i in range(storage.rows)]
        for x,y, radius in [storage[i,0] for i in range(storage.rows)]:
            cv.Circle(out, (x,y), min(7,cv.Round(radius)), cv.CV_RGB(300,1,1), 2)
        #cv.ShowImage("hough", out)

        return circles

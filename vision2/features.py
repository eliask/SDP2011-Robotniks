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

    def computeMoment(self, contour):
        moments = cv.Moments(contour, 1)

        area= cv.GetSpatialMoment(moments,0,0)
        if area == 0: return
        x = cv.GetSpatialMoment(moments,1,0)
        y = cv.GetSpatialMoment(moments,0,1)
        return x,y, area

    def centralMoment(self, img):
        contours = segmentation.get_contours(img)
        if not contours: return
        all_moments = map(self.computeMoment, contours)
        all_moments = filter(lambda x:x is not None, all_moments)
        areas = map(lambda x:x[-1], all_moments)
        center = sum( map(lambda x:np.array(x[:-1]), all_moments) )
        area = sum(areas)
        if area == 0: return
        return center / area

    def getOrientation(self, frame, robot, name, thresh):
        cv.SetImageROI(frame, robot['rect'])
        img = thresh(frame)
        cv.ResetImageROI(frame)
        thresholded_T = cv.CloneImage(img)

        offset = 40
        c = entCenter(robot)
        nhood = ( max(0,int(round(c[0])) - offset),
                  max(0,int(round(c[1])) - offset),
                 2*offset, 2*offset )
        cv.SetImageROI(frame, nhood)
        img2 = self.threshold.dirmarker(frame)
        cv.ResetImageROI(frame)

        def mask_end(img, angle):
            """Mask out one end of the T given an angle of orientation

            Returns a new image.
            """
            X,Y    = entCenter(robot)
            Len,_  = entSize(robot)
            Dist   = 5
            point  = (X + (Dist+Len/2.0)*cos(angle),
                     Y - (Dist+Len/2.0)*sin(angle))
            point  = intPoint(point)
            radius = int(round(Dist + Len/2.0))

            #For visualisation:
            #cv.Circle( frame, point, radius, (0,0,255), 2 )

            rect = entRect(robot)
            point2 = point[0]-rect[0], point[1]-rect[1]
            out = cv.CloneImage(img)
            cv.Circle( out, point2, radius, (0,0,0), -1 )
            return out

        def get_dirmarker(img, angle, Dist, radius):
            X,Y = entCenter(robot)
            Len,_ = entSize(robot)
            point = (X + (Dist+Len/2.0)*cos(angle),
                     Y - (Dist+Len/2.0)*sin(angle))
            point = intPoint(point)

            #For visualisation:
            # cv.Circle( frame, point, radius, (0,200,200), 1 )

            point2 = point[0]-nhood[0], point[1]-nhood[1]
            out = cv.CloneImage(img)
            cv.Zero(out)
            cv.Circle( out, point2, radius, (255,255,255), -1 )

            cv.And(out, img2, out)
            cv.Erode(out,out)
            center = self.centralMoment(out)
            return center

        box_direction = None; max_count = 0
        for angle in entOrientations(robot):
            masked = mask_end(thresholded_T, angle)
            count = cv.CountNonZero(masked)
            if count > max_count:
                max_count = count
                box_direction = angle

        # Not the cleanest way to deal with this angle...
        robot['orient'] = -box_direction

        "Draw the corners of the bounding box"
        for i in getBoxCorners(robot['box']):
            col2=(0,255,255)
            col2=(255,0,0)
            cv.Circle( frame, intPoint(i), 3, col2, -1 )

        dCenter = get_dirmarker( img2, pi-robot['orient'], 8, 10 )
        if dCenter is None:
            dCenter = get_dirmarker( img2, pi-robot['orient'], 10, 4 )
        if dCenter is None:
            dCenter = get_dirmarker( img2, pi-robot['orient'], 14, 8 )
        if dCenter is None:
            dCenter = get_dirmarker( img2, pi-robot['orient'], 18, 4 )
        if dCenter is None:
            dCenter = get_dirmarker( img2, pi-robot['orient'], 18, 8 )
        if dCenter is None:
            return

        dCenter = intPoint(dCenter + nhood[:2])
        cv.Circle(frame, dCenter, 6, (0,0,255), 2)

        Tcenter = self.centralMoment(img)
        if Tcenter is not None:
            Tcenter += entRect(robot)[:2]
            robot['center'] = Tcenter
        else:
            robot['center'] = entCenter(robot)

        cx,cy = robot['center']
        dx,dy = dCenter
        robot['orient'] = atan2(cy-dy, cx-dx)
        #cv.ShowImage(name, img3)

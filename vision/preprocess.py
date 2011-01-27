import cv
import threshold
import logging
from common.utils import *

class Preprocessor:

    #cropRect = (0, 80, 640, 400) # Primary pitch
    cropRect = (0, 45, 640, 400) # Alt. pitch

    bgLearnRate = 0 #.15

    bgsub_kernel = \
        cv.CreateStructuringElementEx(5,5, #size
                                        2,2, #X,Y offsets
                                        cv.CV_SHAPE_RECT)

    def __init__(self, rawSize, threshold, simulator=None):
        self.rawSize = rawSize
        self.cropSize = self.cropRect[2:]
        logging.info( "Captured image size: %s", dim2string(self.rawSize))
        logging.info( "Cropped image size: %s", dim2string(self.cropSize))

        self.initMatrices()

        self.Idistort  = cv.CreateImage(self.rawSize, cv.IPL_DEPTH_8U, 3)

        self.Icrop     = cv.CreateImage(self.cropSize, cv.IPL_DEPTH_8U, 3)
        self.Igray     = cv.CreateImage(self.cropSize, cv.IPL_DEPTH_8U, 1)
        self.Imask     = cv.CreateImage(self.cropSize, cv.IPL_DEPTH_8U, 3)
        self.Iobjects  = cv.CreateImage(self.cropSize, cv.IPL_DEPTH_8U, 3)
        self.bg        = cv.CreateImage(self.cropSize, cv.IPL_DEPTH_8U, 3)
        self.Ieq       = cv.CreateImage(self.cropSize, cv.IPL_DEPTH_8U, 3)
        self.R         = cv.CreateImage(self.cropSize, cv.IPL_DEPTH_8U, 1)
        self.G         = cv.CreateImage(self.cropSize, cv.IPL_DEPTH_8U, 1)
        self.B         = cv.CreateImage(self.cropSize, cv.IPL_DEPTH_8U, 1)

        logging.debug("Loading the background image")
        self.bg = cv.LoadImage('alt-pitch-bg.png')
        logging.debug("Processing the background image:")
        self.bg = cv.CloneImage( self.crop(self.undistort(self.bg)) )
        # cv.SaveImage("calibrated-background.png", self.bg)

        self.standardised = simulator is not None

        self.threshold = threshold

    def standardise(self, frame):
        """Crop and undistort an image, i.e. convert to standard format

        Returns an internal buffer.
        """
        undistorted = self.undistort(frame)
        cropped = self.crop(undistorted)
        return cropped

    def preprocess(self, frame):
        """Preprocess a frame
        :: CvMat -> (CvMat, CvMat, CvMat)

        This method preprocesses a frame by undistorting it using
        prior camera calibration data and then removes the background
        using an image of the background.
        """
        if not self.standardised:
            frame = self.standardise(frame)
        self.continuousLearnBackground(frame)
        bgsub = self.remove_background_values(frame)
        return frame, bgsub, self.threshold.foreground(bgsub)

    def crop(self, frame):
        logging.debug("Cropping a frame")
        sub_region = cv.GetSubRect(frame, self.cropRect)
        cv.Copy(sub_region, self.Icrop)
        return self.Icrop

    def preprocessBG(self, frame):
        ballmask = self.threshold.ball(frame)

    def continuousLearnBackground(self, frame):
        if self.bgLearnRate == 0: return
        cv.AddWeighted(frame, self.bgLearnRate, self.bg,
                         1.0 - self.bgLearnRate, 0, self.bg)

    def remove_background(self, frame):
        """Remove background, leaving robots and some noise.

        It is not safe to modify the returned image, as it will be
        re-initialised each time preprocess is run.
        """
        logging.debug("Performing background subtraction")

        cv.CvtColor(frame, self.Igray, cv.CV_BGR2GRAY)
        cv.Sub(frame, self.bg, self.Imask)

        return self.Imask

    def remove_background_values(self, frame):
        self.Imask = self.remove_background(frame)

        self.Igray = self.threshold.foreground(self.Imask)
        cv.CvtColor(self.Imask, self.Igray, cv.CV_BGR2GRAY)
        cv.EqualizeHist(self.Igray, self.Igray)
        cv.CvtColor(self.Igray, self.Imask, cv.CV_GRAY2BGR)

        #Finally, return the salient bits of the original frame
        cv.And(self.Imask, frame, self.Iobjects)

        return self.Iobjects

    def background_mask(self, frame):
        bgsub_eq = cv.CreateImage(self.pre.cropSize, cv.IPL_DEPTH_8U, 1)
        cv.CvtColor(bgsub, bgsub_eq, cv.CV_BGR2GRAY)
        cv.EqualizeHist(bgsub_eq, bgsub_eq)


    def hist_eq(self, frame):
        cv.Split(frame, self.B, self.G, self.R, None)
        cv.EqualizeHist(self.R, self.R)
        cv.EqualizeHist(self.R, self.B)
        cv.EqualizeHist(self.G, self.G)
        cv.Merge(self.B, self.G, self.R, None, self.Ieq)
        return self.Ieq

    def hsv_normalise(self, frame):
        """Should normalise scene lighting

        Works by setting the HSV Value component to a constant.
        However, turns out that this does not adequately remove shadows.
        Maybe parameter tweaking the Value constant might do something? TODO
        """
        tmp = cv.CreateImage(cv.GetSize(frame), 8, 3)
        cv.CvtColor(frame, tmp, cv.CV_BGR2HSV)

        H,S,V = [ cv.CreateImage(cv.GetSize(frame), 8, 1) for _ in range(3) ]
        cv.Split(tmp, H, S, V, None)

        cv.Set(V, 140)

        cv.Merge(H,S,V, None, tmp);
        cv.CvtColor(tmp, tmp, cv.CV_HSV2BGR),
        out = tmp

        return out

    def undistort(self, frame):
        logging.debug("Undistorting a frame")

        assert frame.width == self.Idistort.width
        assert frame.height == self.Idistort.height

        cv.Undistort2(frame, self.Idistort,
                        self.Intrinsic, self.Distortion)
        return self.Idistort

    def initMatrices(self):
        "Initialise matrices for camera distortion correction."
        logging.debug("Initialising camera matrices")

        dmatL = [ -3.1740235091903346e-01, -8.6157434640872499e-02,
                   9.2026812110876845e-03, 4.4950266773574115e-03 ]

        imatL = [ 8.6980146658682384e+02, 0., 3.7426130495414304e+02,
                  0., 8.7340754327613899e+02, 2.8428760615670581e+02,
                  0., 0., 1. ]

        imat = cv.CreateMat(3,3, cv.CV_32FC1)
        dmat = cv.CreateMat(1,4, cv.CV_32FC1)

        for i in range(3):
            for j in range(3):
                imat[i,j] = imatL[3*i + j]

        for i in range(4):
            dmat[0,i] = dmatL[i]

        self.Distortion = dmat
        self.Intrinsic  = imat

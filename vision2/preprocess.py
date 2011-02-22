import cv
import threshold
import logging
from common.utils import *

class Preprocessor:
    #cropRect = (0, 80, 640, 400) # Primary pitch
    cropRect = (0, 45, 640, 400) # Alt. pitch

    def __init__(self, rawSize, threshold, simulator=None, bg=None, crop=None):
        self.rawSize = rawSize
        if crop:
            self.cropRect = ( self.cropRect[0], self.cropRect[1] + crop[1],
                              self.cropRect[2], crop[3] )
        self.initMatrices()

        self.cropSize = self.cropRect[2:]
        self.standardised = simulator is not None
        self.threshold = threshold

        if rawSize[0] < 600:
            self.cropSize = rawSize

        logging.info( "Captured image size: %s", dim2string(self.rawSize))
        logging.info( "Cropped image size: %s", dim2string(self.cropSize))

        self.Idistort  = cv.CreateImage(self.rawSize, cv.IPL_DEPTH_8U, 3)
        self.Icrop     = cv.CreateImage(self.cropSize, cv.IPL_DEPTH_8U, 3)
        self.Igray     = cv.CreateImage(self.cropSize, cv.IPL_DEPTH_8U, 1)
        self.Imask     = cv.CreateImage(self.cropSize, cv.IPL_DEPTH_8U, 3)
        self.Iobjects  = cv.CreateImage(self.cropSize, cv.IPL_DEPTH_8U, 3)
        self.bg        = cv.CreateImage(self.cropSize, cv.IPL_DEPTH_8U, 3)

        return # background subtraction is not currently used
        if bg:
            logging.debug("Loading dummy background image")
            self.bg = cv.CreateImage(self.rawSize, cv.IPL_DEPTH_8U, 3)
            cv.Zero(self.bg)
        else:
            logging.debug("Loading the background image")
            self.bg = cv.LoadImage('background.jpg')
            logging.debug("Processing the background image:")
            self.bg = cv.CloneImage( self.crop(self.undistort(self.bg)) )

    def get_standard_form(self, frame):
        """Undistort an image, i.e. convert to standard format

        Returns an internal buffer.
        """
        if self.standardised:
            return frame
        else:
            return self.crop( self.undistort(frame) )

    def crop(self, frame):
        logging.debug("Cropping a frame")
        sub_region = cv.GetSubRect(frame, self.cropRect)
        cv.Copy(sub_region, self.Icrop)
        return self.Icrop

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

    def bgsub(self, frame):
        """Preprocess a frame
        :: CvMat -> (CvMat, CvMat, CvMat)

        This method preprocesses a frame by undistorting it using
        prior camera calibration data and then removes the background
        using an image of the background.
        """
        # if not self.standardised:
        #     frame = self.get_standard_form(frame)
        bgsub, mask = self.remove_background_values(frame)
        return bgsub, mask

    def remove_background(self, frame):
        """Remove background, leaving robots and some noise.

        It is not safe to modify the returned image, as it will be
        re-initialised each time preprocess is run.
        """
        logging.debug("Performing background subtraction")
        cv.Sub(frame, self.bg, self.Imask)
        return self.Imask

    def remove_background_values(self, frame):
        self.Imask = self.remove_background(frame)

        logging.debug("Using thresholded background subtracted image as a mask")
        self.Igray = self.threshold.foreground(self.Imask)
        cv.CvtColor(self.Imask, self.Igray, cv.CV_BGR2GRAY)
        cv.Threshold(self.Igray, self.Igray, 200, 255, cv.CV_THRESH_OTSU)
        cv.CvtColor(self.Igray, self.Imask, cv.CV_GRAY2BGR)

        #Finally, return the salient bits of the original frame
        cv.And(self.Imask, frame, self.Iobjects)

        return self.Iobjects, self.Igray

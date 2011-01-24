from opencv import cv, highgui
import threshold

class Preprocessor:

    cropRect = (0, 79, 768, 424)

    bgLearnRate = 0 #.15

    bgsub_kernel = \
        cv.cvCreateStructuringElementEx(5,5, #size
                                        2,2, #X,Y offsets
                                        cv.CV_SHAPE_RECT)

    def __init__(self, rawSize, simulator=None):
        self.rawSize = rawSize
        self.cropSize = cv.cvSize(self.cropRect[2], self.cropRect[3])

        self.initMatrices()
        self.bg = highgui.cvLoadImage('vision/background.png')

        self.Idistort  = cv.cvCreateImage(self.rawSize, cv.IPL_DEPTH_8U, 3)
        self.Icrop     = cv.cvCreateImage(self.cropSize, cv.IPL_DEPTH_8U, 3)
        self.Igray     = cv.cvCreateImage(self.cropSize, cv.IPL_DEPTH_8U, 1)
        self.Imask     = cv.cvCreateImage(self.cropSize, cv.IPL_DEPTH_8U, 3)
        self.Iobjects  = cv.cvCreateImage(self.cropSize, cv.IPL_DEPTH_8U, 3)

        self.bg = self.crop(self.undistort(self.bg))
        # highgui.cvSaveImage("calibrated-background.png", self.bg)

        self.standardised = simulator is not None

    def standardise(self, frame):
        "Crop and undistort an image, i.e. convert to standard format"
        undistorted = self.undistort(frame)
        cropped = self.crop(undistorted)
        return cropped

    def preprocess(self, frame):
        """Preprocess a frame

        This method preprocesses a frame by undistorting it using
        prior camera calibration data and then removes the background
        using an image of the background.
        """
        if not self.standardised:
            frame = self.standardise(frame)

        self.continuousLearnBackground(frame)
        return frame, threshold.robots(frame)

    def crop(self, frame):
        sub_region = cv.cvGetSubRect(frame, self.cropRect)
        cv.cvCopy(sub_region, self.Icrop)
        return self.Icrop

    def preprocessBG(self, frame):
        ballmask = threshold.ball(frame)

    def continuousLearnBackground(self, frame):
        if self.bgLearnRate == 0: return
        cv.cvAddWeighted(frame, self.bgLearnRate, self.bg,
                         1.0 - self.bgLearnRate, 0, self.bg)

    def remove_background(self, frame):
        """Remove background, leaving robots and some noise.

        It is not safe to modify the returned image, as it will be
        re-initialised each time preprocess is run.
        """
        cv.cvCvtColor(frame, self.Igray, cv.CV_BGR2GRAY)
        cv.cvSub(frame, self.bg, self.Imask)

        self.Igray = threshold.robots(self.Imask)
        cv.cvCvtColor(self.Igray, self.Imask, cv.CV_GRAY2BGR)

        #Enlarge the mask a bit to have fewer missing parts due to noise
        cv.cvDilate(self.Imask, self.Imask)

        #This step essentially just reduces the amount of noise
        cv.cvMorphologyEx(self.Imask, self.Imask, None,
                          self.bgsub_kernel, cv.CV_MOP_OPEN)
        cv.cvMorphologyEx(self.Imask, self.Imask, None,
                          self.bgsub_kernel, cv.CV_MOP_CLOSE)

        #Finally, return the salient bits of the original frame
        cv.cvAnd(self.Imask, frame, self.Iobjects)
        return self.Iobjects

    def hsv_normalise(self, frame):
        """Should normalise scene lighting

        Works by setting the HSV Value component to a constant.
        However, turns out that this does not adequately remove shadows.
        Maybe parameter tweaking the Value constant might do something? TODO
        """
        tmp = cv.cvCreateImage(cv.cvGetSize(frame), 8, 3)
        cv.cvCvtColor(frame, tmp, cv.CV_BGR2HSV)

        H,S,V = [ cv.cvCreateImage(cv.cvGetSize(frame), 8, 1) for _ in range(3) ]
        cv.cvSplit(tmp, H, S, V, None)

        cv.cvSet(V, 140)

        cv.cvMerge(H,S,V, None, tmp);
        cv.cvCvtColor(tmp, tmp, cv.CV_HSV2BGR),
        out = tmp

        return out

    def undistort(self, frame):
        cv.cvUndistort2(frame, self.Idistort, self.Intrinsic, self.Distortion)
        return self.Idistort

    def initMatrices(self):
        "Initialise matrices for camera distortion correction."

        dmatL = [ -3.1740235091903346e-01, -8.6157434640872499e-02,
                   9.2026812110876845e-03, 4.4950266773574115e-03 ]

        imatL = [ 8.6980146658682384e+02, 0., 3.7426130495414304e+02,
                  0., 8.7340754327613899e+02, 2.8428760615670581e+02,
                  0., 0., 1. ]

        imat = cv.cvCreateMat(3,3, cv.CV_32F)
        dmat = cv.cvCreateMat(4,1, cv.CV_32F)

        for i in range(3):
            for j in range(3):
                imat[i][j] = imatL[3*i + j]

        for i in range(4):
            dmat[i] = dmatL[i]

        self.Distortion = dmat
        self.Intrinsic  = imat

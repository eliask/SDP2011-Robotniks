import pickle
from opencv import cv, highgui
import threshold

class Preprocessor:

    # Intrinsic and Distortion matrices are stored in the file:
    MATRIX_FILE = 'correctionmatrix.dat'

    def __init__(self, size):
        self.size = size
        self.loadMatrices()

        self.pitch_mask = highgui.cvLoadImage('pitch_mask.png')
        self.bg = highgui.cvLoadImage('background.png')

        self.Igray     = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
        self.Imask     = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 3)
        self.Iobjects  = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 3)

        self.bgsub_kernel = \
            cv.cvCreateStructuringElementEx(5, 5, #size
                                            2, 2, #X,Y offsets
                                            cv.CV_SHAPE_RECT)

    def preprocess(self, frame):
        """Preprocess a frame

        This method preprocesses a frame by undistorting it using
        prior camera calibration data and then removes the background
        using an image with no objects.
        """
        #TODO: crop the unused bits of the image
        #subimage = cvGetSubRect(frame, cvRect( 0, 0, sz.width, sz.height ))

        #new = self.undistort(frame)
        new = frame
        return self.remove_background(new)

    def remove_background(self, frame):
        """Remove background, leaving foreground objects and some noise.

        It is not safe to modify the returned image, as it will be
        re-initialised each time preprocess is run.
        """
        cv.cvAnd(frame, self.pitch_mask, frame)
        cv.cvCvtColor(frame, self.Igray, cv.CV_BGR2GRAY)
        cv.cvSub(frame, self.bg, self.Imask)

        self.Igray = threshold.foreground(self.Imask)
        cv.cvCvtColor(self.Igray, self.Imask, cv.CV_GRAY2BGR)

        #Enlarge the mask a bit to account eliminate missing parts due to noise
        cv.cvDilate(self.Imask, self.Imask)

        #This step essentially just reduces the amount of noise
        cv.cvMorphologyEx(self.Imask, self.Imask, None, self.bgsub_kernel, cv.CV_MOP_OPEN)
        cv.cvMorphologyEx(self.Imask, self.Imask, None, self.bgsub_kernel, cv.CV_MOP_CLOSE)

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
        out = cv.cvCreateImage(self.size, cv.IPL_DEPTH_8U, 3)
        cv.cvUndistort2(frame, out, self.Intrinsic, self.Distortion)
        return out

    def loadMatrices(self):
        "Load matrices for barrel distortion correction."
        with open(self.MATRIX_FILE, 'r') as input:
            #(self.Intrinsic, self.Distortion) = pickle.load(input)
            (ilist, dlist) = pickle.load(input)

            imat = cv.cvCreateMat(3,3,1111638021)
            dmat = cv.cvCreateMat(4,1,1111638021)
            for i in range(3):
                for j in range(3):
                    imat[i][j] = ilist[i][j]
            for i in range(4):
                dmat[i] = dlist[i]
            self.Intrinsic = imat
            self.Distortion = dmat

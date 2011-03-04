import cv

T = ['tmp', [0,0,0], [0,0,0]]
trackbar_window=None
def createTrackbars(window):
    def set1a(x): T[1][0]=x
    def set2a(x): T[1][1]=x
    def set3a(x): T[1][2]=x
    def set1z(x): T[2][0]=x
    def set2z(x): T[2][1]=x
    def set3z(x): T[2][2]=x

    global trackbar_window
    trackbar_window = window
    cv.CreateTrackbar("ch1 min", window, T[1][0], 255, set1a)
    cv.CreateTrackbar("ch2 min", window, T[1][1], 255, set2a)
    cv.CreateTrackbar("ch3 min", window, T[1][2], 255, set3a)

    cv.CreateTrackbar("ch1 max", window, T[2][0], 255, set1z)
    cv.CreateTrackbar("ch2 max", window, T[2][1], 255, set2z)
    cv.CreateTrackbar("ch3 max", window, T[2][2], 255, set3z)

def setValues(threshold):
    """Adds trackbars to the main window for adjusting thresholding values

    Optionally uses some other window (specified by 'window').
    """
    global current
    current = threshold

    for i,v in enumerate(threshold[1]):
        T[1][i] = v
        if trackbar_window:
            cv.SetTrackbarPos("ch%d min"%(i+1), trackbar_window, v)
    for i,v in enumerate(threshold[2]):
        T[2][i] = v
        if trackbar_window:
            cv.SetTrackbarPos("ch%d max"%(i+1), trackbar_window, v)

def updateValues():
    for i,v in enumerate(current[1]):
        current[1][i] = T[1][i]
    for i,v in enumerate(current[2]):
        current[2][i] = T[2][i]

class Base(object):

    colorspaceConv = \
        { 'bgr' : lambda x: x,
          'hsv' : lambda x: cv.CvtColor(x, x, cv.CV_BGR2HSV),
          'hls' : lambda x: cv.CvtColor(x, x, cv.CV_BGR2HLS),
          }

    @classmethod
    def ball(self, frame):
        """Return the mask for the ball.

        Very good detection rate from full background and extremely few
        false positives.
        """
        return self.threshold(frame, self.Tball, magic=True)

    @classmethod
    def blueT(self, frame):
        "Return the mask for the blue T."
        return self.threshold(frame, self.Tblue, magic=True)

    @classmethod
    def yellowT(self, frame):
        "Outputs a mask containing the yellow T."
        return self.threshold(frame, self.Tyellow, magic=True)

    @classmethod
    def dirmarker(self, frame):
        return self.threshold(frame, self.Tdirmarker, magic=True)

    @classmethod
    def threshold(self, frame, record, op=cv.And, magic=False):
        """Threshold a frame using a record of min/max thresholds

        Output is a new image.
        """
        colorspace, min, max = record

        tmp = cv.CloneImage(frame)
        if magic:
            cv.Smooth(tmp, tmp, cv.CV_GAUSSIAN, 5)
        # Work in the correct colorspace
        self.colorspaceConv[colorspace](tmp)

        num_chans = len(min)
        size = cv.GetSize(frame)
        chan = [ cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
                 for _ in range(num_chans) ]
        cv.Split(tmp, chan[0], chan[1], chan[2], None)

        minS = map(cv.Scalar, min)
        maxS = map(cv.Scalar, max)
        for i in range(num_chans):
            cv.InRangeS(chan[i], minS[i], maxS[i], chan[i])

        out = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
        op(chan[0], chan[1], out)
        op(out, chan[2], out)

        return out

class PrimaryRaw(Base):
    Tblue      = [ 'hsv', [84,  108,  108 ], [132, 255, 255] ]
    Tyellow    = [ 'hsv', [14,   54,  235 ], [ 45, 255, 255] ]
    Tball      = [ 'bgr', [0,    0,   164 ], [126, 146, 255] ]
    Tdirmarker = [ 'bgr', [0,    22,   22 ], [144, 160, 164] ]

class AltRaw(Base):
    Tblue      = [ 'hsv', [84,  108,  108 ], [132, 255, 255] ]
    Tyellow    = [ 'hsv', [14,   54,  220 ], [ 45, 255, 255] ]
    Tball      = [ 'bgr', [50,   50,  130 ], [130, 122, 255] ]
    Tdirmarker = [ 'bgr', [25,   25,   25 ], [110, 150, 100] ]

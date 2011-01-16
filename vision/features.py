from opencv import cv, highgui

class Features:

    colorspaceConv = \
        { 'bgr' : lambda x: x,
          'hsv' : lambda x: cv.cvCvtColor(x, x, cv.CV_BGR2HSV),
        }

    # Thresholds for all entities
    # Format: color space, minima, maxima (per channel)

    ###Useless
    #Tyellow    = ( 'bgr', (170,   240,  240 ), (210,  255, 255) )
    # 247 red & green is a good identifier in normal lighting
    # also identifies the ball and stuff; requires BG sub.
    Tyellow    = ( 'hsv', (0,   90,  90 ), (40,  255, 255) )

    # loads of noise and NO dirmarker
    Tdirmarker = ( 'bgr', (0,   0,   0  ), (100, 100, 100) )
    #Tbackplate = ( 'hsv', (30,  30,  100), (100, 255, 255) )

    # Identifies the outlines of the robots
    #TODO: the threshold should be determined dynamically from
    #      the histogram; i.e. should cover the last "valley"
    Tbackplate = ( 'bgr', (0,  166,  0  ), (255, 242, 255) )
    # Identifies bits of the ball
    Tball      = ( 'bgr', (0,   0,   140), (110, 110, 255) )
    # Works reasonably; the T is somewhat noisy though
    Tblue      = ( 'hsv', (80,  70,  90 ), (140, 255, 255) )

    @classmethod
    def threshold(self, frame, record, op=cv.cvAnd):
        "Threshold a frame using a record of min/max thresholds"
        colorspace, min, max = record

        tmp = cv.cvCloneImage(frame)
        # Work in the correct colorspace
        # TODO: somewhat inefficient converting the colorspace anew each time
        self.colorspaceConv[colorspace](tmp)

        size = cv.cvGetSize(frame)
        num_chans = len(min)
        chan = [ cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
                 for _ in range(num_chans) ]

        cv.cvSplit(tmp, chan[0], chan[1], chan[2], None)

        minS = map(cv.cvScalar, min)
        maxS = map(cv.cvScalar, max)
        for i in range(3):
            cv.cvInRangeS(chan[i], minS[i], maxS[i], chan[i])

        out = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
        op(chan[0], chan[1], out)
        op(out, chan[2], out)

        return out

    @classmethod
    def playerPositions(self, frame):
        highgui.cvSaveImage("Tblue.png", self.threshold(frame, self.Tblue))
        highgui.cvSaveImage("Tyellow.png", self.threshold(frame, self.Tyellow))
        highgui.cvSaveImage("Tbackplate.png", self.threshold(frame, self.Tbackplate))

        # self.threshold(frame, self.Tblue)
        # self.threshold(frame, self.Tyellow)
        # self.threshold(frame, self.Tbackplate)

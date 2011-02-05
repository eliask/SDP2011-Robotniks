import cv

class Base(object):
    colorspaceConv = \
        { 'bgr' : lambda x: x,
          'hsv' : lambda x: cv.CvtColor(x, x, cv.CV_BGR2HSV),
          'hls' : lambda x: cv.CvtColor(x, x, cv.CV_BGR2HLS),
          }

    @classmethod
    def foreground(self, frame):
        return self.threshold(frame, self.Tforeground, op=cv.Or)

    @classmethod
    def robots(self, frame):
        """Returns a mask that mostly covers the robots.

        Very few false positives.
        """
        return self.threshold(frame, self.Trobots, op=cv.Or)

    @classmethod
    def ball(self, frame):
        """Return the mask for the ball.

        Very good detection rate from full background and extremely few
        false positives.
        """
        return self.threshold(frame, self.Tball, magic=True)

    @classmethod
    def blueT(self, frame):
        """Return the mask for the blue T.

        Very good detection rate from full background and extremely few
        false positives.
        """
        return self.threshold(frame, self.Tblue, magic=True)

    @classmethod
    def yellowT(self, frame):
        """Outputs a mask containing the yellow T.

        The dimensions of the T are roughly 32 x 42 pixels.
        """
        return self.threshold(frame, self.Tyellow, magic=True)

    @classmethod
    def dirmarker(self, frame):
        return self.threshold(frame, self.Tdirmarker, magic=True)

    @classmethod
    def backplate(self, frame):
        return self.threshold(frame, self.Tbackplate)

    @classmethod
    def threshold(self, frame, record, op=cv.And, magic=False):
        """Threshold a frame using a record of min/max thresholds

        Output is a new image.
        """
        colorspace, min, max = record

        tmp = cv.CloneImage(frame)
        if magic:
            cv.Smooth(tmp, tmp, cv.CV_GAUSSIAN, 11)
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

    @classmethod
    def thresholdGray(self, gray):
        "A more efficient (?) thresholding for gray stuff"
        #cv.Threshold(gray, ...)
        pass


class RandomRaw(Base):
    # Thresholds for all entities
    # Format: color space, minima, maxima (per channel)

    Tyellow = ( 'hsv', (18,  140, 120), (50,  255, 255) )

    # Both work with false positive regions
    Tdirmarker  = ( 'hsv', [10,   0,   80 ], [ 90,  90, 145] )
    Tdirmarker  = ( 'bgr', [70,   90,  70 ], [115, 150, 130] )

    # Identifies the outlines of the robots
    Tbackplate  = ( 'bgr', [100, 200,  80 ], [180, 255, 140] )
    #Tball       = ( 'bgr', [0,   0,   140], [110, 110, 255] )
    #Tblue       = ( 'hsv', [80,  70,  90 ], [140, 255, 255] )
    Trobots = ( 'bgr', [255,  200,  255], [255, 255, 255] )
    Tforeground = ( 'bgr', [35,  20,  20], [255, 255, 255] )

class PrimaryRaw(Base):
    #Primary pitch:
    Tball       = ( 'bgr', [40,   60,   160], [110, 110, 255] )
    Tblue       = ( 'bgr', [150,  130,  85 ], [210, 185, 180] )
    Tblue2      = ( 'bgr', [150,  185,  90 ], [255, 255, 160] )
    Tblue       = ( 'bgr', [170,  140,  105 ], [225, 210, 125] )
    Tyellow     = ( 'bgr', [50,  165,  180 ], [165, 255, 255] )

    # Effectively return only foreground objects (+ a little noise)
    Trobots = ( 'bgr', [255,  185,  255], [255, 255, 255] )
    Tdirmarker  = ( 'bgr', [75,   110,  75 ], [110, 160, 110] ) #w/magic

    Tball       = ( 'bgr', [40,   60,   160], [110, 110, 255] )
    Tball       = ( 'bgr', [130,  10,   200], [255, 110, 255] )
    Tblue       = ( 'bgr', [170,  140,  70 ], [255, 210, 255] )
    Tyellow     = ( 'bgr', [70,  180,  225 ], [255, 255, 255] )

    # Effectively return only foreground objects (+ a little noise)
    Trobots = ( 'bgr', [255,  185,  255], [255, 255, 255] )
    Tdirmarker  = ( 'bgr', [75,   110,  75 ], [110, 160, 110] ) #w/magic
    Tdirmarker  = ( 'bgr', [75,   100,  85 ], [120, 150, 120] ) #w/magic
    Tforeground = ( 'bgr', [35,  20,  20 ], [255, 255, 255] )
    Tforeground = ( 'bgr', [190, 190, 190], [255, 255, 255] )
    #foreground = [30,45,60]

    Tball       = ( 'bgr', [40,   60,   160], [110, 110, 255] )
    Tball       = ( 'bgr', [130,  10,   200], [255, 110, 255] )
    Tball       = ( 'bgr', [0,  0,   115], [255, 115, 255] )
    Tblue       = ( 'bgr', [170,  140,  70 ], [255, 210, 255] )
    Tyellow     = ( 'bgr', [70,  180,  225 ], [255, 255, 255] )

    # Effectively return only foreground objects (+ a little noise)
    Trobots = ( 'bgr', [255,  185,  255], [255, 255, 255] )
    Tdirmarker  = ( 'bgr', [75,   110,  75 ], [110, 160, 110] ) #w/magic
    Tdirmarker  = ( 'bgr', [75,   100,  85 ], [120, 150, 120] ) #w/magic
    Tdirmarker  = ( 'bgr', [65,   80,  55 ], [120, 150, 120] ) #w/magic
    Tforeground = ( 'bgr', [35,  20,  20 ], [255, 255, 255] )
    #Tforeground = ( 'bgr', [190, 190, 190], [255, 255, 255] )
    #foreground = [30,45,60]


class AltRaw(Base):
    Tball       = [ 'bgr', [40,   60,   160], [110, 110, 255] ]
    # ch2,ch3 min. can be ~0:
    Tblue       = ( 'bgr', [125,  70,  90 ], [255, 190, 255] )
    Tyellow     = [ 'bgr', [0,  200,  0 ], [255, 255, 255] ]

    # Effectively return only foreground objects (+ a little noise)
    Trobots = [ 'bgr', [255,  185,  255], [255, 255, 255] ]
    Tdirmarker  = ( 'bgr', [75,   110,  75 ], [110, 160, 110] ) #w/magic
    Tdirmarker  = ( 'bgr', [75,   100,  85 ], [120, 150, 120] ) #w/magic
    Tdirmarker  = [ 'bgr', [65,   80,  55 ], [120, 150, 120] ] #w/magic
    Tforeground = [ 'bgr', [2,  17,  46 ], [255, 255, 255] ]
    Tforeground = [ 'bgr', [190, 190, 190], [255, 255, 255] ]
    Tfg = [ 'bgr', [10,10,10], [91,91,91]]
    #foreground = [30,45,60]

    Tblue       = [ 'bgr', [125,  70,  90 ], [255, 190, 255] ]
    Tcustom     = [ 'bgr', [125,  70,  90 ], [255, 190, 255] ]

    @classmethod
    def custom(self, image):
        return self.threshold(frame, self.Tcustom)

    def updateThresholds(self, hist_props):
        B,G,R = hist_props

        # The plateaus of the histogram don't actually seem to provide
        # very much useful information, especially since they
        # fluctuate.
        platB, platG, platR = map(lambda x:x['plateaus'], hist_props)

        ppB, ppG, ppR = map(lambda x:x['post_peaks'], hist_props)
        #print "GLOBAL:", ppB, ppG, ppR
        # print hist_props[0]
        # print hist_props[1]
        # print hist_props[2]
        #platG[min(0, len(platG))], platR[min(0,len(platR))]]
        if len(platG) > 2: gMin = platG[1]
        else: gMin = 0
        if len(platR) > 2: rMin = platR[1]
        else: rMin = 0
        #if len(platB) >
        for i in platB:
            if ppB+20 < i: ppB = i; break
        self.Tblue[1] = [min(ppB, B[98]), G[25], R[0]]
        self.Tblue[2] = [255, 255, R[50]]

        self.Tyellow[1] = [0, 5+max(ppG, R[99]), 5+max(ppR, R[99])]
        self.Tyellow[2] = [255, 255, 255]

        self.Tball[1] = [0, 0, max(ppR, R[95])]
        self.Tball[2] = [B[80], R[80], 255]

        # prim
        self.Tdirmarker[1] = [B[15], G[20], R[15]]
        self.Tdirmarker[2] = [B[35], G[35], R[35]]

        # alt
        self.Tdirmarker[1] = [B[30], G[30], R[30]]
        self.Tdirmarker[2] = [B[50], G[40], R[50]]

        self.Tforeground[1] = [ppG, ppB, ppR]
        self.Tforeground[1] = [B[self.Tfg[1][0]], G[self.Tfg[1][1]], R[self.Tfg[1][2]]]
        #self.Tforeground[2] = [B[self.Tfg[2][0]], G[self.Tfg[2][1]], R[self.Tfg[2][2]]]

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

        # cv.ReleaseImage(tmp)
        # #TODO: Why does this cause a segfault?
        # map(cv.ReleaseImage, chan)

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
    Tball       = ( 'bgr', [40,   60,   160], [110, 110, 255] )
    # ch2,ch3 min. can be ~0:
    Tblue       = ( 'bgr', [125,  70,  90 ], [255, 190, 255] )
    Tyellow     = ( 'bgr', [0,  200,  0 ], [255, 255, 255] )

    # Effectively return only foreground objects (+ a little noise)
    Trobots = ( 'bgr', [255,  185,  255], [255, 255, 255] )
    Tdirmarker  = ( 'bgr', [75,   110,  75 ], [110, 160, 110] ) #w/magic
    Tdirmarker  = ( 'bgr', [75,   100,  85 ], [120, 150, 120] ) #w/magic
    Tdirmarker  = ( 'bgr', [65,   80,  55 ], [120, 150, 120] ) #w/magic
    Tforeground = ( 'bgr', [2,  17,  46 ], [255, 255, 255] )
    #Tforeground = ( 'bgr', [190, 190, 190], [255, 255, 255] )
    #foreground = [30,45,60]

    Tblue       = ( 'bgr', [125,  70,  90 ], [255, 190, 255] )

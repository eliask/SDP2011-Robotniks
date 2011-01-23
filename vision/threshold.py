from opencv import cv

colorspaceConv = \
    { 'bgr' : lambda x: x,
      'hsv' : lambda x: cv.cvCvtColor(x, x, cv.CV_BGR2HSV),
    }

# Thresholds for all entities
# Format: color space, minima, maxima (per channel)

Tyellow = ( 'hsv', (18,  140, 120), (50,  255, 255) )

# Both work with false positive regions
Tdirmarker  = ( 'hsv', [10,   0,   80 ], [ 90,  90, 145] )
Tdirmarker  = ( 'bgr', [70,   90,  70 ], [115, 150, 130] )

# Identifies the outlines of the robots
Tbackplate  = ( 'bgr', [100, 200,  80 ], [180, 255, 140] )
Tball       = ( 'bgr', [0,   0,   140], [110, 110, 255] )
Tblue       = ( 'hsv', [80,  70,  90 ], [140, 255, 255] )

# Effectively return only foreground objects (+ a little noise)
Trobots = ( 'bgr', [255,  200,  255], [255, 255, 255] )

def robots(frame):
    """Returns a mask that mostly covers the robots.

    Very few false positives.
    """
    return threshold(frame, Trobots, op=cv.cvOr)

def ball(frame):
    """Return the mask for the ball.

    Very good detection rate from full background and extremely few
    false positives.
    """
    return threshold(frame, Tball, magic=True)

def blueT(frame):
    """Return the mask for the blue T.

    Very good detection rate from full background and extremely few
    false positives.
    """
    return threshold(frame, Tblue, magic=True)

def yellowT(frame):
    """Outputs a mask containing the yellow T.

    The dimensions of the T are roughly 32 x 42 pixels.
    """
    return threshold(frame, Tyellow, magic=True)

def dirmarker(frame):
    return threshold(frame, Tdirmarker)

def backplate(frame):
    return threshold(frame, Tbackplate)

def threshold(frame, record, op=cv.cvAnd, magic=False):
    """Threshold a frame using a record of min/max thresholds

    Output is a new image.
    """
    colorspace, min, max = record

    tmp = cv.cvCloneImage(frame)
    if magic:
        cv.cvSmooth(tmp, tmp, cv.CV_GAUSSIAN, 11)
    # Work in the correct colorspace
    colorspaceConv[colorspace](tmp)

    num_chans = len(min)
    size = cv.cvGetSize(frame)
    chan = [ cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
             for _ in range(num_chans) ]
    cv.cvSplit(tmp, chan[0], chan[1], chan[2], None)

    minS = map(cv.cvScalar, min)
    maxS = map(cv.cvScalar, max)
    for i in range(num_chans):
        cv.cvInRangeS(chan[i], minS[i], maxS[i], chan[i])

    out = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
    op(chan[0], chan[1], out)
    op(out, chan[2], out)

    # cv.cvReleaseImage(tmp)
    # #TODO: Why does this cause a segfault?
    # map(cv.cvReleaseImage, chan)

    return out

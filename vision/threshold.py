from opencv import cv

colorspaceConv = \
    { 'bgr' : lambda x: x,
      'hsv' : lambda x: cv.cvCvtColor(x, x, cv.CV_BGR2HSV),
    }

# Thresholds for all entities
# Format: color space, minima, maxima (per channel)

# 247 red & green is a good identifier in normal lighting
# also identifies the ball and stuff; requires BG sub.
TyellowAndBall     = ( 'hsv', (0,   90,  90 ), (40,  255, 255) )

# Works somewhat when away from the edges/shadows
Tdirmarker  = ( 'bgr', (0,   0,   0  ), (100, 100, 100) )

# Identifies the outlines of the robots
#TODO: the threshold should be determined dynamically from
#      the histogram; i.e. should cover the last "valley"
Tbackplate  = ( 'bgr', (0,  166,  0  ), (255, 242, 255) )
# Identifies bits of the ball
Tball       = ( 'bgr', (0,   0,   140), (110, 110, 255) )
# Works reasonably; the T is somewhat noisy though
Tblue       = ( 'hsv', (80,  70,  90 ), (140, 255, 255) )

# Effectively return only foreground objects (+ a little noise)
Tforeground = ( 'bgr', (35,  10,  20 ), (255, 255, 255) )

def foreground(frame):
    return threshold(frame, Tforeground, op=cv.cvOr)

def yellowTAndBall(frame):
    """Outputs a mask containing the yellow T and the ball

    The dimensions of the T are roughly 32 x 42 pixels.
    The ball is around 12 to 17 pixels in diameter (being a blob
    that's not entirely circle-looking)
    """
    return threshold(frame, TyellowAndBall, magic=True)

def ball(frame):
    """
    Works much like yellowTAndBall, but the return mask is more
    compact and better matches the shape of the ball.
    """
    return threshold(frame, Tball, magic=True)

def blueT(frame):
    return threshold(frame, Tblue, magic=True)

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

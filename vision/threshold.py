from opencv import cv

colorspaceConv = \
    { 'bgr' : lambda x: x,
      'hsv' : lambda x: cv.cvCvtColor(x, x, cv.CV_BGR2HSV),
    }

# Thresholds for all entities
# Format: color space, minima, maxima (per channel)

###Useless
# One picture gives the values (106, 217, 138) for backplates
#Gives a rough noisy outline -- almost useless
#Tbackplate  = ( 'bgr', (50,  100,  100 ), (150, 255, 190) )

#Tyellow     = ( 'bgr', (170,   240,  240 ), (210,  255, 255) )
# 247 red & green is a good identifier in normal lighting
# also identifies the ball and stuff; requires BG sub.

TyellowAndBall     = ( 'hsv', (0,   90,  90 ), (40,  255, 255) )

# loads of noise and NO dirmarker
Tdirmarker  = ( 'bgr', (0,   0,   0  ), (100, 100, 100) )
#Tbackplate  = ( 'hsv', (30,  30,  100), (100, 255, 255) )

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

yellow_kernel = \
    cv.cvCreateStructuringElementEx(7,7,
                                    3,3, #X,Y offsets
                                    cv.CV_SHAPE_CROSS)
def yellowTAndBall(frame):
    """Outputs a mask containing the yellow T and the ball

    The dimensions of the T are roughly 32 x 42 pixels.
    The ball is around 12 to 17 pixels in diameter (being a blob
    that's not entirely circle-looking)
    """
    mask = threshold(frame, TyellowAndBall)
    cv.cvDilate(mask, mask, yellow_kernel)
    cv.cvErode(mask, mask, yellow_kernel)
    return mask

def yellowT(frame):
    # Doesn't work well
    raise NotImplementedError

    # mask = threshold(frame, TyellowAndBall)
    mask = yellowTAndBall(frame)
    # TODO: some duplication of effort
    cv.cvXor(ball(frame), mask, mask)
    return mask

ball_kernel = \
    cv.cvCreateStructuringElementEx(4,4,
                                    2,2, #X,Y offsets
                                    cv.CV_SHAPE_CROSS)
def ball(frame):
    """
    Works much like yellowTAndBall, but the return mask is more
    compact and better matches the shape of the ball.
    """
    mask = threshold(frame, Tball)
    cv.cvDilate(mask, mask, ball_kernel)
    cv.cvErode(mask, mask, ball_kernel)
    return mask

def blueT(frame):
     mask = threshold(frame, Tblue)
     cv.cvDilate(mask, mask, ball_kernel)
     cv.cvErode(mask, mask, ball_kernel)
     return mask


dir_kernel = \
    cv.cvCreateStructuringElementEx(7,7,
                                    3,3, #X,Y offsets
                                    cv.CV_SHAPE_RECT)
def dirmarker(frame):
    return threshold(frame, Tdirmarker)

def backplate(frame):
    return threshold(frame, Tbackplate)

image_buffers = []
def get_image_buffers(num_chans, size):
    if len(image_buffers) < num_chans:
        image_buffers.extend(
            [ cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
              for _ in range(num_chans - len(image_buffers)) ] )

    return image_buffers[:num_chans]

def threshold(frame, record, op=cv.cvAnd):
    """Threshold a frame using a record of min/max thresholds

    Output is a new image.
    """
    colorspace, min, max = record

    tmp = cv.cvCloneImage(frame)
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

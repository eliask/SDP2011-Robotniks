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

Tyellow     = ( 'hsv', (0,   90,  90 ), (40,  255, 255) )

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

def ball(frame):
    return threshold(frame, Tball)

def yellowT(frame):
    return threshold(frame, Tyellow)

def blueT(frame):
    return threshold(frame, Tblue)

kernel = cv.cvCreateStructuringElementEx(7, 7,
                                         2,2, #X,Y offsets
                                         cv.CV_SHAPE_RECT)
def dirmarker(frame):
    #TODO: figure out some way to find the black spot amidst the black background

    gray = cv.cvCreateImage(cv.cvGetSize(frame), cv.IPL_DEPTH_8U, 1)
    cv.cvCvtColor(frame, gray, cv.CV_BGR2GRAY)
    out = threshold(frame, Tdirmarker)
    #cv.cvCvtColor(out, gray, cv.CV_BGR2GRAY)
    #cv.cvSmooth (out, out, cv.CV_BLUR, 5,5, 0)
    #cv.cvCanny(out, out, 5, 15, 3)
    #edge = cv.cvCreateImage(cv.cvGetSize(frame), cv.IPL_DEPTH_CV32F, 1)
    # cv.cvCvtColor(frame, gray, cv.CV_GRAY232F)
    # cv.cvSobel(gray, out, 1,1, 3)
    return out

    # An alternative implementation:

    # size = cv.cvGetSize(frame)

    # gray, tmp, mask = get_image_buffers(3, size)
    # cv.cvThreshold(gray, mask, 0, 255, cv.CV_THRESH_BINARY)
    # cv.cvDilate(mask, mask, kernel)
    # cv.cvThreshold(gray, tmp, 100, 255, cv.CV_THRESH_BINARY_INV)

    # out = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
    # cv.cvAnd(tmp, mask, out)

    #return out

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
    "Threshold a frame using a record of min/max thresholds"
    colorspace, min, max = record

    tmp = cv.cvCloneImage(frame)
    # Work in the correct colorspace
    # TODO: somewhat inefficient converting the colorspace anew each time
    colorspaceConv[colorspace](tmp)

    num_chans = len(min)
    size = cv.cvGetSize(frame)
    chan = get_image_buffers(num_chans, size)
    cv.cvSplit(tmp, chan[0], chan[1], chan[2], None)

    minS = map(cv.cvScalar, min)
    maxS = map(cv.cvScalar, max)
    for i in range(num_chans):
        cv.cvInRangeS(chan[i], minS[i], maxS[i], chan[i])

    out = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
    op(chan[0], chan[1], out)
    op(out, chan[2], out)

    return out

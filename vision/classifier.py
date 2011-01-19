import math
from utils import *

class Entity:
    dist = 10000
    A = None
    B = None

    def __init__(self, A, B, dist):
        self.dist = dist
        self.A = A
        self.B = B

class Robot(Entity):
    dirmarker = None
    T = None


def classify(pos):
    """
    :: dict( label -> [ (CvBox2D, CvRect) ] )
       -> dict( label -> (CvBox2D, CvBox2D) )

    Takes as input the positions of the detected features.

    Outputs the positions of the ball and the robots, coupled with
    their features, such as the bounding box of the direction marker
    and the coloured T. Either of the markers could potentially be
    missing from the output, but we do as much as we can here to infer
    some of the missing features.

    Below is a description of the position entities gives as input:

    objects - any foreground objects that remain after background
              subtraction -- extremely reliable at detecting the
              objects, but contains some noisy bits too at random
              places.

    yellow - the yellow T and the ball. The yellow T should be first
             in the list and should only be missing if it is missing
             from the picture. The ball

    blue   - The blue T and little else. Should be very reliable. In all
             normal circumstances, the blue T will be first in the list,
             as it should be the largest feature.

    ball   - The ball and probably nothing else. Very reliable at
             detecting the ball. Again, in normal circumstances the
             actual ball should be first on the list.
    """

    entities = {}
    for name in ['yellow', 'blue', 'ball']:
        entities[name] = Entity(None, None, 1000)

    def getBoxes(struct):
        return [ x[0] for x in struct ]
    def getClosest(theBox, name):
        boxes = getBoxes(pos[name])
        if len(boxes) == 0:
            return entities[name]
        s = sorted(boxes, key=lambda x: boxDist(theBox, x))
        print name, "stuff:", (map (lambda x: boxDist(theBox, x), s))
        dist = boxDist(theBox, s[0])
        if dist < entities[name].dist:
            return Entity(theBox, s[0], dist)

    for oBox in getBoxes(pos['blue']):
        blueT_Body = getClosest(oBox, 'objects')

    for oBox in getBoxes(pos['ball']):
        ball = getClosest(oBox, 'objects')
        yellowAndBall = getClosest(oBox, 'yellow')

    for oBox in getBoxes(pos['yellow']):
        yellowT_Body = getClosest(oBox, 'objects')

    for oBox in getBoxes(pos['dirmarker']):
        yellowT_Body = getClosest(oBox, 'objects')

    # TODO: is == defined?
    if yellowT_Body == yellowAndBall:
        print "The yellow T appears to be the same as the ball mask D:"

    # What if?
    # - blue/yellow lack dirmarkers?
    if not pos['yellow'] or
    # - yellow is missing?
    # - blue is missing?
    # - ball is missing?

    entities['blue']   = blueT_Body
    entities['yellow'] = yellowT_Body
    entities['ball']   = ball


    # for oBox in getBoxes
    #
    #         entities[name] =
    # for oBox in getBoxes(pos['objects']):
    #     entities['ball'] = getClosest(, 'yellow')

    print "Balls found:", len(pos['ball'])

    return entities

    # entities['ball'] = [ x
    #                      for x in pos['ball']
    #                      for y in pos['ball']
    #                      if boxDist(x, y) < BALL_MAX_DIST ]

def boxDist(A, B):
    x1, y1 =  BoxCenterPos(A)
    x2, y2 =  BoxCenterPos(B)
    return math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )

def getCenters():
    """
    [ (CvBox2D, CvRect) ] ) -> dict( label -> (CvBox2D, CvRect) )
    """
    pass

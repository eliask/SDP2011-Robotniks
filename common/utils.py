try:
    import cv
except ImportError:
    pass

import pygame
import tempfile
from math import *
import numpy as np


def entDimPos(ent):
    """Outputs a tuple of strings for entity size and position
    :: Entity -> ( String(size), String(position) )
    """
    return entDimString(ent), entPosString(ent)
def entDimString(ent):
    return pos2string(entSize(ent))
def entPosString(ent):
    return pos2string(entCenter(ent))
def pos2string(pos):
    return "(%d, %d)" % (pos[0], pos[1])

def entSize(ent):
    """Return entity size

    Here, size is defined as the longer dimension times the shorter
    dimension ("width x height" if you will)
    """
    box = ent['box']
    width, height = max(box[1]), min(box[1])
    return width, height

epsilon = 1e-3
def approxZero(num, epsilon=epsilon):
    return abs(num) < epsilon

def entCenter(ent):
    return boxCenter(ent['box'])
def boxCenter(box):
    return np.array(box[0])
def entRect(ent):
    return np.array(ent['rect'])
def rectPos(rect):
    return rect[:2]
def rectSize(rect):
    return rect[2:]

def robotAngle(robot):
    return robot['box'][2]

def entDim(ent):
    return boxDim(ent['box'])
def boxDim(box):
    return np.array(box[1])

def entOrientation(ent):
    """Return two possible orientations for an entity in radians
    :: Ent -> [angle, angle]

    We use the fact the all entities of interest point to some
    direction (or its opposite) by being longer in that direction. If
    the entity has a square bounding box, we return the empty list.
    """
    angle = entAngle(ent)
    w,h = entDim(ent)
    if w == h:
        return [] # or raise Exception?
    elif w > h:
        angles = [angle, angle+pi]
    else:
        angles = [angle+pi/2, angle-pi/2]

    return angles

def entAngle(ent):
    "The orientation of the entity's bounding box in (-pi/2, pi)"
    return boxAngle(ent['box'])
def boxAngle(box):
    """The orientation of the bounding box in (-pi/2, pi)

    We negate the sign due to:
    http://tech.groups.yahoo.com/group/OpenCV/message/54146:
    * "box.angle" appears to be the angle in degrees through which the
    points are rotated CLOCKWISE about "box.center"
    """
    return radians(-box[2])

def getArea(box):
    return box[1][0] * box[1][1]

def inBox(parent, child):
    child_pos = entCenter(child)
    assert 'box' in parent, "Entity must have a bounding box"
    corners = getBoxCorners(parent['box'])
    return pointInConvexPolygon(corners, child_pos)

def pointInConvexPolygon(points, point):
    """Determine whether a point is within a convex polygon.

    We are using method 3 from:
    http://local.wasp.uwa.edu.au/~pbourke/geometry/insidepoly/

    If a point is on a line, we consider it to still be inside the
    polygon.
    """
    x,y = point
    previous = 0
    for p0, p1 in zip( points, points[-1:] + points[1:] ):
        x0,y0 = p0; x1,y1 = p1
        # If the point is always on the same side of a line formed by
        # traversing the edges made by joining up the points of the
        # polygon, it is within the polygon
        side = (y-y0)*(x1-x0) - (x-x0)*(y1-y0)

        if side < 0 and previous > 0: # to the right
            return False
        if side > 0 and previous < 0: # to the right
            return False
        previous = side

    # Every point so far has been on the same side of the lines
    return True

def getBoxCorners(box):
    center = boxCenter(box)
    topleft = center - boxDim(box)/2.0
    W,H = boxDim(box)
    unrot = [ topleft, topleft+(W,0), topleft+(W,H), topleft+(0,H) ]
    # TODO: verify that the angle is correct
    rotated = rotatePoints( unrot, center, boxAngle(box) )
    return rotated

def imSize(im):
    return (im.width, im.height)

def Point(x, y):
    return cv.Point( int(x), int(y) )

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

def dist(src, dest):
    return sqrt( sum((src-dest)**2) )

def getAnglePi(angle):
    "Return an angle in [-pi, pi]"
    return angle % -pi
    assert -pi <= new <= pi, \
        "Angle not within specifications: %f" % new
    return new

def inRange(x, y, z):
    return x < y < z or x > y > z

def clamp(_min, val, _max):
    return min(_max, max(_min, val))

def rotatePoints(points, center, angle):
    "Rotate points around center by an angle"

    # Any nicer way to do this?
    M = [ [], [], [] ]
    for x, y in points:
        M[0].append(x)
        M[1].append(y)
        M[2].append(1)

    Points = np.matrix(M)
    Trans1 = np.matrix([ [ 1, 0, center[0] ],
                         [ 0, 1, center[1] ],
                         [ 0, 0, 1 ] ])
    Trans2 = np.matrix([ [ 1, 0, -center[0] ],
                         [ 0, 1, -center[1] ],
                         [ 0, 0, 1 ] ])
    Rotate = np.matrix([[ cos(angle), -sin(angle), 1 ],
                        [ sin(angle),  cos(angle), 1 ],
                        [      0,           0,     1 ] ])

    Transform = Trans1 * Rotate * Trans2
    Rotated = Transform * Points
    # print Points
    # print Rotated

    return map(np.array,
               zip(Rotated[0].tolist()[0], Rotated[1].tolist()[0]) )


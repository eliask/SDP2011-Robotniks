from opencv import cv, highgui
import pygame
import tempfile
from math import *
import numpy as np

epsilon = 1e-3
def approxZero(num, epsilon=epsilon):
    return abs(num) < epsilon

def centerPos(ent):
    return (ent['box'].center.x, ent['box'].center.y)

def getArea(box):
    return box.size.width * box.size.height

def Point(x, y):
    return cv.cvPoint( int(x), int(y) )

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

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

    return zip( Rotated[0].tolist()[0], Rotated[1].tolist()[0] )


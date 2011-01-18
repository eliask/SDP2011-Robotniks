from opencv import cv

def BoxCenterPos(point):
    return (point.center.x, point.center.y)

def getBoxArea(box):
    return box.size.width * box.size.height

def Point(x, y):
    return cv.cvPoint( int(x), int(y) )

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

def BoxCenterPos(point):
    return (point.center.x, point.center.y)

def getBoxArea(box):
    return box.size.width * box.size.height

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

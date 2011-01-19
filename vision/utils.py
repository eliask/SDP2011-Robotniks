from opencv import cv, highgui
import math

def BoxCenterPos(point):
    return (point.center.x, point.center.y)

def getBoxArea(box):
    return box.size.width * box.size.height

def Point(x, y):
    return cv.cvPoint( int(x), int(y) )

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

def PygameToCVImage(self, pg_img):
    tmp = tempfile.mktemp()
    pygame.image.tostring(pg_img, tmp)
    frame = highgui.cvLoadImage(tmp)
    return frame

def CVtoPygameImage(self, frame):
    rgb = cv.CreateMat(frame.height, frame.width, cv.CV_8UC3)
    cv.CvtColor(frame, rgb, cv.CV_BGR2RGB)
    pg_img = pygame.image.frombuffer(rgb.tostring(), cv.GetSize(rgb), "RGB")
    return pg_img

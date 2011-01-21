from opencv import cv, highgui
import pygame
import tempfile
import math

def centerPos(ent):
    return (ent['box'].center.x, ent['box'].center.y)

def getArea(box):
    return box.size.width * box.size.height

def Point(x, y):
    return cv.cvPoint( int(x), int(y) )

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

def CVtoPygameImage(self, frame):
    rgb = cv.CreateMat(frame.height, frame.width, cv.CV_8UC3)
    cv.CvtColor(frame, rgb, cv.CV_BGR2RGB)
    pg_img = pygame.image.frombuffer(rgb.tostring(), cv.GetSize(rgb), "RGB")
    return pg_img

def clamp(_min, val, _max):
    return min(_max, max(_min, val))
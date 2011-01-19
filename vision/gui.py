from opencv import cv, highgui
import pygame
import tempfile
from utils import *

class GUI:
    entities = {}

    # Run the main program until we decide to quit
    quit = False

    def __init__(self):
        pass

    def update(self, frame, pos):
        img = CVtoPygameImage(frame)
        self.drawEntities(frame, pos)
        highgui.cvShowImage(self.WindowName, frame)
        self.processInput()

    def drawRotBox(self, ent):
        if ent is None: return
        box=ent.B
        if box is None: return

        x,y = BoxCenterPos(box)
        radius = box.size.width

    def drawEntities(self, frame, ents):
        self.frame = frame
        self.drawRotBox(ents['yellow'], color=cv.CV_RGB(255,255,0), label='YELLOW')
        self.drawRotBox(ents['blue'], color=cv.CV_RGB(0,128,255), label='BLUE')
        self.drawRotBox(ents['ball'], color=cv.CV_RGB(255,0,255), label='BALL')

    def processInput(self):
        pass

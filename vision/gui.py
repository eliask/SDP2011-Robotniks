from opencv import cv, highgui
from utils import *
from math import *

class GUI:

    WindowName = 'Camera'

    # Run the main program until we decide to quit
    quit = False

    def __init__(self):
        highgui.cvNamedWindow(self.WindowName)

    def __del__(self):
        highgui.cvDestroyAllWindows()

    def update(self, frame, ents):
        self.drawEntities(frame, ents)
        highgui.cvShowImage(self.WindowName, frame)
        self.processInput()

    def drawRotBox(self, ent, color=cv.CV_RGB(255,128,0), label="UNNAMED"):
        if not ent:
            print label
            return
        if type(ent) == list and len(ent) > 0:
            ent = ent[0]
        #print ent
        x,y = BoxCenter(ent)
        radius = ent['box'].size.width
        cv.cvCircle(self.frame, Point(x, y), cv.cvRound(min(15,radius)), color)

        if 'orient' in ent and ent['orient']:
            o = ent['orient']
            cv.cvCircle(self.frame, Point(x+50*cos(o), y+50*sin(o)),
                        cv.cvRound(min(15,radius)), cv.CV_RGB(200,200,200))

        R = ent['rect']
        cv.cvRectangle(self.frame, cv.cvPoint(int(R.x), int(R.y)),
                     cv.cvPoint(int(R.x + R.width), int(R.y + R.height)),
                     color, 2, 8, 0)

    def drawEntities(self, frame, ents):
        self.frame = frame
        self.drawRotBox(ents['balls'], color=cv.CV_RGB(255,0,255), label='BALL')

        if ents['yellow']:
            print "Y:", ents['yellow']['box'].angle
            self.drawRotBox(ents['yellow'], color=cv.CV_RGB(255,255,64), label='YELLOW')
            self.drawRotBox(ents['yellow']['T'], color=cv.CV_RGB(200,200,64), label='YELLOW T')
            self.drawRotBox(ents['yellow']['dirmarker'],
                            color=cv.CV_RGB(100,100,0), label='YELLOW DIR')

        if ents['blue']:
            print "B:",ents['blue']['box'].angle
            self.drawRotBox(ents['blue'], color=cv.CV_RGB(64,64,255), label='BLUE')
            self.drawRotBox(ents['blue']['T'], color=cv.CV_RGB(200,64,255), label='BLUE T')
            self.drawRotBox(ents['blue']['dirmarker'],
                            color=cv.CV_RGB(0,0,100), label='BLUE DIR')

    def processInput(self):
        k = highgui.cvWaitKey(5)
        if k == '\x1b':
            self.quit = True
        elif k == 's':
            filename = time.strftime('%y%m%d-%H%M-%S.png')
            highgui.cvSaveImage(filename, self.frame)
            print filename + ' saved.'


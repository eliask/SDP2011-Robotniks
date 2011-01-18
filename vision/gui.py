from opencv import cv, highgui
from utils import *

class GUI:

    # Window name to show video stream in
    WindowName = 'Camera'

    # Colors for entities
    Colors = {'Yellow'    : cv.CV_RGB(255, 255, 0),
              'Blue'      : cv.CV_RGB(0, 0, 255),
              'Backplate' : cv.CV_RGB(0, 255, 0),
              'Ball'      : cv.CV_RGB(255, 0, 0),
              'Direction' : cv.CV_RGB(0, 255, 255)}

    # Font for overlays
    Font = cv.cvInitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.4, 0.4, 0, 1, 8)

    entities = {}

    # Run the main program until we decide to quit
    quit = False

    def __init__(self):
        highgui.cvNamedWindow(self.WindowName)

    def __del__(self):
        highgui.cvDestroyAllWindows()

    def update(self, frame, pos):
        self.drawEntities(frame, pos)
        highgui.cvShowImage(self.WindowName, frame)
        self.processInput()

    def drawRotBox(self, ent, color=cv.CV_RGB(255,128,0), label="UNNAMED"):
        "Draws CvBox2D in current frame"
        if ent is None: return
        box=ent.B
        if box is None: return

        x,y = BoxCenterPos(box)
        radius = box.size.width
        cv.cvCircle(self.frame, Point(x, y), cv.cvRound(min(15,radius)), color)

    def drawEntities(self, frame, ents):
        self.frame = frame
        self.drawRotBox(ents['yellow'], color=cv.CV_RGB(255,255,0), label='YELLOW')
        self.drawRotBox(ents['blue'], color=cv.CV_RGB(0,128,255), label='BLUE')
        self.drawRotBox(ents['ball'], color=cv.CV_RGB(255,0,255), label='BALL')

    def processInput(self):
        k = highgui.cvWaitKey(5)
        if k == '\x1b':
            self.quit = True
        elif k == 's':
            filename = time.strftime('snapshots/%y%m%d-%H%M-%S.png')
            highgui.cvSaveImage(filename, self.frame)
            print filename + ' saved.'

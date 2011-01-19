from opencv import cv, highgui
from utils import *

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
        x,y = BoxCenterPos(ent['box'])
        radius = ent['box'].size.width
        cv.cvCircle(self.frame, Point(x, y), cv.cvRound(min(15,radius)), color)

        if 'dirmarker' in ent and ent['dirmarker']:
            dirx, diry = BoxCenterPos(ent['dirmarker']['box'])
            dx, dy = x - dirx, y - diry
            print "DELTA:",  dx, dy
            cv.cvCircle(self.frame, Point(x+3*dx, y+3*dy), cv.cvRound(min(15,radius)), cv.CV_RGB(200,200,200))


        R = ent['rect']
        #sub = cv.cvGetSubRect(self.frame, (R.x, R.y, R.width, R.height))
        cv.cvRectangle(self.frame, cv.cvPoint(int(R.x), int(R.y)),
                     cv.cvPoint(int(R.x + R.width), int(R.y + R.height)),
                     color, 2, 8, 0)

    def drawEntities(self, frame, ents):
        self.frame = frame
        self.drawRotBox(ents['balls'], color=cv.CV_RGB(255,0,255), label='BALL')

        if ents['yellow']:
            self.convertRobotCoordinates(ents['yellow'])
            self.drawRotBox(ents['yellow'], color=cv.CV_RGB(255,255,64), label='YELLOW')
            self.drawRotBox(ents['yellow']['T'], color=cv.CV_RGB(200,200,64), label='YELLOW')
            self.drawRotBox(ents['yellow']['dirmarker'],
                            color=cv.CV_RGB(100,100,0), label='YELLOW')

        if ents['blue']:
            self.convertRobotCoordinates(ents['blue'])
            self.drawRotBox(ents['blue'], color=cv.CV_RGB(64,64,255), label='BLUE')
            self.drawRotBox(ents['blue']['T'], color=cv.CV_RGB(200,64,255), label='BLUE')
            self.drawRotBox(ents['blue']['dirmarker'],
                            color=cv.CV_RGB(0,0,100), label='BLUE')

    def convertRobotCoordinates(self, robot):
        if robot['T']:
            self.convertCoordinates(robot, robot['T'])
        if robot['dirmarker']:
            self.convertCoordinates(robot, robot['dirmarker'])

    def convertCoordinates(self, ent, sub):
        "Convert relative coordinates to absolute"
        C = ent['box'].center
        R = ent['rect']
        c = sub['box'].center
        sub['box'].center.x = c.x + R.x # ~ roughly correct
        sub['box'].center.y = c.y + R.y # but TODO: fix or verify
        r = sub['rect']
        sub['rect'].x = r.x + R.x
        sub['rect'].y = r.y + R.y

    def processInput(self):
        k = highgui.cvWaitKey(5)
        if k == '\x1b':
            self.quit = True
        elif k == 's':
            filename = time.strftime('%y%m%d-%H%M-%S.png')
            highgui.cvSaveImage(filename, self.frame)
            print filename + ' saved.'


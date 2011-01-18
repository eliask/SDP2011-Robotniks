#from . import *
import sys
from opencv import cv, highgui

from capture import *
from preprocess import *
import features
import classifier
from gui import *
import random
import time

winMap = {}
def updateWin(name, frame):
    if not winMap.has_key(name):
        winMap[name] = \
        {'window' : highgui.cvNamedWindow(name, highgui.CV_WINDOW_AUTOSIZE)}
    highgui.cvShowImage(name, frame)

class Vision():

    Size = cv.cvSize(768, 576)

    def __init__(self, args):
        self.capture = Capture(self.Size, args[-1])
        self.pre = Preprocessor(self.Size)
        #self.world = World()
        self.UI = GUI()

    def run(self):
        times=[]
        N=0
        while not self.UI.quit and N < 50:
            print "Frame:", N
            N+=1
            start= time.clock()
            frame = self.capture.getFrame()
            frame = self.pre.preprocess(frame)
            positions = features.extract_features(frame)

            for o in positions.values():
                for box2d, rect in o:
                    x,y = BoxCenterPos(box2d)
                    radius = box2d.size.width
                    cv.cvCircle(frame, Point(x, y), cv.cvRound(min(30,radius)),
                                cv.CV_RGB(random.randint(1,255),
                                          random.randint(1,255),
                                          random.randint(1,255)) )

            ents = classifier.classify(positions)
            self.UI.update(frame, ents)
            #self.world.update()
            end= time.clock()
            times.append( (end-start) )

        print "Time:", sum(times)/N * 25

if __name__ == "__main__":
    v = Vision(sys.argv)
    v.run()


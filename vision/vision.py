import sys
from opencv import cv, highgui
from capture import *
from preprocess import *
from features import FeatureExtraction
from gui import *
import random
import time

class Vision():
    Size = cv.cvSize(768, 576)

    def __init__(self, args):
        self.capture = Capture(self.Size, args[-1])
        self.pre = Preprocessor(self.Size)
        self.featureEx = FeatureExtraction(self.Size)
        self.UI = GUI()

    def run(self):
        times=[]
        N=0
        while not self.UI.quit and N < 500:
            print "Frame:", N
            N+=1
            start= time.clock()
            frame = self.capture.getFrame()
            print "preprocess"
            frame = self.pre.preprocess(frame)
            print "features"
            ents = self.featureEx.features(frame)

            self.UI.update(frame, ents)
            end= time.clock()
            times.append( (end-start) )

        print "Runtime/realtime ratio:", sum(times)/N * 25

if __name__ == "__main__":
    v = Vision(sys.argv)
    v.run()


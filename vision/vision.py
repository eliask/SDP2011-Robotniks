import sys
from opencv import cv, highgui
from capture import *
from preprocess import *
from features import FeatureExtraction
from interpret import Interpreter
from world import World
from gui import *
import random
import time
import math

class Vision():
    rawSize = cv.cvSize(768, 576)

    def __init__(self, args):
        self.capture = Capture(self.rawSize, args[-1])
        self.pre = Preprocessor(self.rawSize)
        self.featureEx = FeatureExtraction(self.pre.cropSize)
        self.interpreter = Interpreter()
        self.world = World()
        self.UI = GUI()

    def run(self):
        times=[]
        N=0
        while not self.UI.quit: # and N < 500:
            print "Frame:", N
            N+=1
            startTime = time.time()

            frame = self.capture.getFrame()
            print "preprocess"
            frame, processed = self.pre.preprocess(frame)
            print "features"
            ents = self.featureEx.features(processed)
            self.interpreter.interpret(ents)
            self.world.update(startTime, ents)
            self.UI.update(frame, ents)

            endTime = time.time()
            times.append( (endTime - startTime) )

        avg = sum(times)/N
        print "Runtime/realtime ratio:", avg * 25
        print "Avg. processing time / frame: %.2f ms" % (avg * 1000)
        print "Standard deviation: %.2f ms" % \
            ( 1000*math.sqrt(sum(map(lambda x:(x-avg)**2, times)) / N) )

if __name__ == "__main__":
    v = Vision(sys.argv)
    v.run()


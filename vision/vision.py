from opencv import cv, highgui
from capture import Capture
from simcapture import SimCapture
from preprocess import Preprocessor
from features import FeatureExtraction
from interpret import Interpreter
from common.world import World
from common.gui import GUI
import random, time, math
import debug

class Vision():
    rawSize = cv.cvSize(768, 576)

    def __init__(self, filename=None, simulator=None):
        if simulator:
            self.capture = SimCapture(simulator)
        else:
            self.capture = Capture(self.rawSize, filename)

        self.pre = Preprocessor(self.rawSize, simulator)
        self.featureEx = FeatureExtraction(self.pre.cropSize)
        self.interpreter = Interpreter()
        self.world = World()
        self.UI = GUI()

        self.times=[]
        self.N=0

    def processFrame(self):
        print "Frame:", self.N
        self.N += 1
        startTime = time.time()
        frame = self.capture.getFrame()
        print "preprocess"
        frame, robotMask = self.pre.preprocess(frame)
        print "features"
        ents = self.featureEx.features(frame, robotMask)
        self.interpreter.interpret(ents)
        self.world.update(startTime, ents)
        self.UI.update(frame, ents)

        endTime = time.time()
        self.times.append( (endTime - startTime) )

    def run(self):
        while not self.UI.quit: # and N < 500:
            self.processFrame()

        avg = sum(times)/N
        print "Runtime/realtime ratio:", avg * 25
        print "Avg. processing time / frame: %.2f ms" % (avg * 1000)
        print "Standard deviation: %.2f ms" % \
            ( 1000*math.sqrt(sum(map(lambda x:(x-avg)**2, times)) / N) )

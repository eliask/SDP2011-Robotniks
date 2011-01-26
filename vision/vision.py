from opencv import cv, highgui
from capture import Capture
from simcapture import SimCapture
from preprocess import Preprocessor
from features import FeatureExtraction
from interpret import Interpreter
from common.world import World
from common.gui import GUI
import random, time, math, logging
import debug

class Vision():
    rawSize = cv.cvSize(640, 480)

    def __init__(self, world, filename=None, simulator=None):
        if simulator:
            self.capture = SimCapture(simulator)
        else:
            self.capture = Capture(self.rawSize, filename)

        self.pre = Preprocessor(self.rawSize, simulator)
        self.featureEx = FeatureExtraction(self.pre.cropSize)
        self.interpreter = Interpreter()
        self.world = world
        self.UI = GUI()

        self.times=[]
        self.N=0

        import threshold
        self.threshold = threshold.PrimaryRelative
        debug.thresholdValues(self.threshold.Tdirmarker)

    def processFrame(self):
        startTime = time.time()
        logging.debug("Time:", startTime)
        logging.debug("Frame:", self.N)
        self.N += 1

        frame = self.capture.getFrame()
        logging.debug("Entering preprocessing")
        standard, bgsub, mask = self.pre.preprocess(frame)
        logging.debug("Entering feature extraction")
        ents = self.featureEx.features(bgsub, self.threshold)
        logging.debug("Detected entities:", ents)
        logging.debug("Entering interpreter")
        self.interpreter.interpret(ents)
        logging.debug("Entering interpreter")
        self.world.update(startTime, ents)
        self.UI.update(standard, ents)

        endTime = time.time()
        self.times.append( (endTime - startTime) )

    def run(self):
        while not self.UI.quit: # and N < 500:
            self.processFrame()

    def runtimeInfo(self):
        avg = 1000*sum(times)/N # in milliseconds
        variance = sum(map(lambda x:(x-avg)**2, times)) / N
        stddev = math.sqrt(variance)
        logging.info( "Runtime/realtime ratio:", avg * 25/1000 )
        logging.info( "Avg. processing time / frame: %.2f ms", avg )
        logging.info( "Standard deviation: %.2f ms", stddev )

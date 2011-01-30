import cv
from capture import Capture
from simcapture import SimCapture
from preprocess import Preprocessor
from features import FeatureExtraction
from interpret import Interpreter
from common.world import World
from common.gui import GUI
import threshold
import random, time, math, logging
import debug

T=[0, [150,150,150],[30,30,30]]
class Vision():
    #rawSize = (768,576)
    rawSize = (640, 480)

    def __init__(self, world, filename=None, simulator=None):
        logging.info('Initialising vision')
        if simulator:
            self.capture = SimCapture(simulator)
        else:
            self.capture = Capture(self.rawSize, filename)

        self.threshold = threshold.AltRaw
        self.pre = Preprocessor(self.rawSize, self.threshold, simulator)
        self.featureEx = FeatureExtraction(self.pre.cropSize)
        self.interpreter = Interpreter()
        self.world = world
        self.gui = GUI(world, self.pre.cropSize, self.threshold)

        self.times=[]
        self.N=0

        logging.debug('Vision initialised')

    def processFrame(self):
        startTime = time.time()
        logging.debug("Frame %d at %f", self.N, startTime)
        self.N += 1

        logging.debug("Capturing a frame")
        frame = self.capture.getFrame()
        logging.debug("Entering preprocessing")
        standard, bgsub_vals, bgsub_mask = self.pre.preprocess(frame)
        logging.debug("Entering feature extraction")
        ents = self.featureEx.features(bgsub_vals, self.threshold)
        logging.debug("Detected entities:", ents)
        logging.debug("Entering interpreter")
        self.interpreter.interpret(ents)
        logging.debug("Entering interpreter")
        self.world.update(startTime, ents)

        bgsub = self.pre.remove_background(standard)
        self.gui.updateWindow('raw', frame)
        self.gui.updateWindow('mask', bgsub_mask)
        self.gui.updateWindow('foreground', bgsub_vals)
        self.gui.updateWindow('bgsub', bgsub)
        self.gui.updateWindow('standard', standard)
        self.gui.draw(ents, startTime)
        endTime = time.time()

        self.times.append( (endTime - startTime) )

    def run(self):
        logging.debug("Entering the main loop")
        while not self.gui.quit: # and N < 500:
            self.processFrame()
        self.runtimeInfo()

    def runtimeInfo(self):
        avg = 1000*sum(times)/N # in milliseconds
        variance = sum(map(lambda x:(x-avg)**2, times)) / N
        stddev = math.sqrt(variance)
        logging.info( "Runtime/realtime ratio:", avg * 25/1000 )
        logging.info( "Avg. processing time / frame: %.2f ms", avg )
        logging.info( "Standard deviation: %.2f ms", stddev )

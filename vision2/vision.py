import cv
from capture import Capture, EOF
from preprocess import Preprocessor
from features import FeatureExtraction
from common.world import World
from gui import GUI
import threshold
import random, time, math, logging

inf=1e1000
class Vision():
    rawSize = (640, 480)

    def __init__(self, world, filenames=None, simulator=None,
                 once=False, headless=False):
        logging.info('Initialising vision')
        self.headless = headless
        self.capture = Capture(self.rawSize, filenames, once)
        self.threshold = threshold.AltRaw()
        self.world = world
        self.simulator = simulator

        self.initComponents()
        self.times=[]
        self.N=0
        logging.debug('Vision initialised')

    def initComponents(self, crop=None):
        undistort = False
        self.pre = Preprocessor(self.rawSize, self.threshold,
                                undistort, crop=crop)
        self.featureEx = FeatureExtraction(self.pre.cropSize)
        self.gui = GUI(self.world, self.pre.cropSize, self.threshold, self)
        self.world.setResolution(self.pre.cropSize)

    def formatTime(self, t):
        return time.strftime('%H:%M:%S', time.localtime(t)) \
            + ( '%.3f' % (t - math.floor(t)) )[1:] #discard leading 0

    def processFrame(self):
        startTime = time.time()
        logging.debug("Frame %d at %s", self.N,
                      self.formatTime(startTime) )
        self.N += 1

        logging.debug("Capturing a frame")
        frame = self.capture.getFrame()
        logging.debug("Entering preprocessing")
        standard = self.pre.get_standard_form(frame)
        logging.debug("Entering feature extraction")

        ents = self.featureEx.features(standard, self.threshold)
        logging.debug("Detected entities:", ents)
        logging.debug("Entering World")
        self.world.update(startTime, ents)

        logging.debug("Updating GUI")
        if not self.headless:
            try:
                self.gui.updateWindow('raw', frame)
                self.gui.updateWindow('standard', standard)
                self.gui.draw(ents, startTime)
            except Exception, e:
                logging.error("GUI failed: %s", e)
                raise

        endTime = time.time()
        self.times.append( (endTime - startTime) )

    def run(self, skip=0, until=inf):
        logging.debug("Entering the main loop")

        try:
            if skip > 0:
                logging.debug("Skipping the first %d frames", skip)
            for _ in range(skip):
                self.capture.getFrame()

            while not self.gui.quit and self.N < until:
                self.processFrame()
        except EOF:
            pass

        self.runtimeInfo()

    def runtimeInfo(self):
        avg = 1000*sum(self.times)/self.N # in milliseconds
        variance = sum(map(lambda x:(x-avg)**2, self.times)) / self.N
        stddev = math.sqrt(variance)
        logging.info( "Runtime/realtime ratio: %.3f", avg * 25/1000 )
        logging.info( "Avg. processing time / frame: %.2f ms", avg )
        logging.info( "Standard deviation: %.2f ms", stddev )
        logging.info( "Avg. FPS: %.2f", 1000/avg )

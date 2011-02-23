import cv
from capture import Capture
from simcapture import SimCapture
from mplayer_capture import MPlayerCapture
from preprocess import Preprocessor
from features import FeatureExtraction
from interpret import Interpreter
from histogram import Histogram
from common.world import World
from common.gui import GUI
import threshold
import random, time, math, logging
import debug

T=[0, [150,150,150],[30,30,30]]
class Vision():
    #rawSize = (768,576)
    rawSize = (640, 480)

    # Whether to 'crash' when something non-critical like the GUI fails
    debug = True

    def __init__(self, world, filename=None, simulator=None):
        logging.info('Initialising vision')
        if simulator:
            self.capture = SimCapture(simulator)
        else:
            self.capture = MPlayerCapture(self.rawSize, filename)
            #self.capture = Capture(self.rawSize, filename)

        self.threshold = threshold.PrimaryRaw()
        self.pre = Preprocessor(self.rawSize, self.threshold, simulator)
        self.featureEx = FeatureExtraction(self.pre.cropSize)
        self.interpreter = Interpreter()
        self.world = world
        self.gui = GUI(world, self.pre.cropSize, self.threshold)
        self.histogram = Histogram(self.pre.cropSize)

        self.times=[]
        self.N=0

        debug.thresholdValues(self.threshold.Tfg, self.gui)

        logging.debug('Vision initialised')

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
        standard, bgsub_vals, bgsub_mask = self.pre.preprocess(frame)
        logging.debug("Entering feature extraction")

        hist_props_bgsub = self.histogram.calcHistogram(standard)
        hist_props_abs = self.histogram.calcHistogram(bgsub_vals)
        self.threshold.updateBGSubThresholds(hist_props_bgsub)
        #self.threshold.updateAbsThresholds(hist_props_abs)

        ents = self.featureEx.features(standard, self.threshold)
        #ents = self.featureEx.features(bgsub_vals, self.threshold)
        logging.debug("Detected entities:", ents)
        logging.debug("Entering interpreter")
        self.interpreter.interpret(ents)
        logging.debug("Entering interpreter")
        self.world.update(startTime, ents)

        try:
            bgsub = self.pre.remove_background(standard)
            self.gui.updateWindow('raw', frame)
            self.gui.updateWindow('mask', bgsub_mask)
            self.gui.updateWindow('foreground', bgsub_vals)
            self.gui.updateWindow('bgsub', bgsub)
            self.gui.updateWindow('standard', standard)
            canny = cv.CreateImage(self.pre.cropSize, 8,1)
            # adaptive = cv.CreateImage(self.pre.cropSize, 32,3)
            # tmp = cv.CreateImage(self.pre.cropSize, 8,3)
            # cv.Convert(standard, adaptive)
            cv.CvtColor(bgsub, canny, cv.CV_BGR2GRAY)
            cv.Threshold(canny, canny, 150, 255, cv.CV_THRESH_OTSU)
            # cv.Threshold(canny, canny, 100, 255, cv.CV_ADAPTIVE_THRESH_GAUSSIAN_C)
            # cv.Sobel(adaptive, adaptive, 1,1,1)
            # cv.Convert(adaptive, tmp)
            # cv.ConvertScale(tmp, tmp, 10)
            # cv.CvtColor(tmp, canny, cv.CV_BGR2GRAY)
            # cv.Threshold(canny,canny, 50, 255, cv.CV_THRESH_BINARY)
            cv.Canny(canny,canny, 100, 180,3)

            self.gui.updateWindow('adaptive', canny)
            self.gui.draw(ents, startTime)
        except Exception, e:
            logging.error("GUI failed: %s", e)
            if self.debug:
                raise

        endTime = time.time()
        self.times.append( (endTime - startTime) )

    def run(self):
        logging.debug("Entering the main loop")
        while not self.gui.quit: # and N < 500:
            self.processFrame()
        self.runtimeInfo()

    def runtimeInfo(self):
        avg = 1000*sum(self.times)/self.N # in milliseconds
        variance = sum(map(lambda x:(x-avg)**2, self.times)) / self.N
        stddev = math.sqrt(variance)
        logging.info( "Runtime/realtime ratio: %.3f", avg * 25/1000 )
        logging.info( "Avg. processing time / frame: %.2f ms", avg )
        logging.info( "Standard deviation: %.2f ms", stddev )
        logging.info( "Avg. FPS: %.2f", 1000/avg )

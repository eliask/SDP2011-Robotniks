import cv
from vision.mplayer_capture import MPlayerCapture
from common.gui import GUI
import time, logging

class BasicVision():
    #rawSize = (768,576)
    rawSize = (640, 480)

    def __init__(self, world, filename=None, simulator=None, once=False, headless=False):
        logging.info('Initialising vision')
        #required on DICE:
        self.capture = MPlayerCapture(self.rawSize, filename, once)

        self.gui = GUI(world, self.pre.cropSize, self.threshold)
        logging.debug('Vision initialised')

    def processFrame(self):
        logging.debug("Capturing a frame")
        startTime = time.time()
        frame = self.capture.getFrame()
        ents = {}

        logging.debug("Updating GUI")
        self.gui.updateWindow('raw', frame)
        self.gui.draw(ents, startTime)

    def run(self):
        while not self.gui.quit:
            self.processFrame()

if __name__ == '__main__':
    v = BasicVision()
    v.run()

import cv
from vision.mplayer_capture import MPlayerCapture
from vision.preprocess import Preprocessor
from common.gui import GUI
import vision.threshold
import time, logging
from common.world import World

class BasicVision():
    #rawSize = (768,576)
    rawSize = (640, 480)

    def __init__(self):
        logging.info('Initialising vision')
        #required on DICE:
        self.capture = MPlayerCapture(self.rawSize)

        world = World('blue') # arbitrary colour
        world.pointer=None

        self.threshold = vision.threshold.AltRaw()
        self.pre = Preprocessor(self.rawSize, self.threshold, None)
        self.gui = GUI(world, self.rawSize, self.threshold)
        logging.debug('Vision initialised')

    def processFrame(self):
        logging.debug("Capturing a frame")
        startTime = time.time()
        frame = self.capture.getFrame()
        ents = {'yellow':None, 'blue':None, 'balls':[]}

        logging.debug("Updating GUI")
        self.gui.updateWindow('standard', frame)
        self.gui.updateWindow('foreground', frame)
        self.gui.draw(ents, startTime)

    def run(self):
        while not self.gui.quit:
            self.processFrame()

if __name__ == '__main__':
    v = BasicVision()
    v.run()

#from . import *
import sys
from opencv import cv, highgui

class Vision():

    def __init__(self, args):
        self.capture = Capture(args[-1])
        self.pre = Preprocessor()
        #self.world = World()
        self.UI = GUI()

    def run(self):
        while not self.UI.quit:
            frame = self.capture.getFrame()
            self.pre.preprocess(frame)
            #features.extract_features()
            self.classifier.classify()
            self.world.update()
            self.UI.update()

if __name__ == "__main__":
    v = Vision()
    v.run(sys.argv)


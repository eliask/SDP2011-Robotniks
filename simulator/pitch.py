from world import World
from vision.preprocess import Preprocessor
from vision.capture import Capture
from vision.vision import Vision
import os, tempfile
from .common.utils import *

class OpenCVPitch(Capture):

    def __init__(self, filename=None, once=False):
        Capture.__init__(self, Vision.rawSize, filename)
        self.tmpfile = tempfile.mktemp(suffix='.bmp')
        self.once = once
        self.pre = Preprocessor(Vision.rawSize)

    def __del__(self):
        os.remove(self.tmpfile)

    def get(self):
        # In case we want a recorded video background to loop, try to
        # re-initialise the capture.
        try:
            frame = self.getFrame()
        except Capture.CaptureFailure:
            if self.once:
                raise
            self.initCapture()
            frame = self.getFrame()

        # Remove distortions from the raw image
        frame = self.pre.standardise(frame)

        highgui.cvSaveImage(self.tmpfile, frame)
        return pygame.image.load(self.tmpfile)

class StaticPitch:
    def __init__(self, filename):
        self.pitch = pygame.image.load(filename)
    def get(self):
        return self.pitch

class SolidPitch(StaticPitch):
    def __init__(self, colour=(0,0,0,0)):
        self.pitch = pygame.surface.Surface(World.Resolution)
        self.pitch.fill(colour)


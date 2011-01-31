from world import World
from vision.preprocess import Preprocessor
from vision.capture import *
from vision.vision import Vision
import os, tempfile
from common.utils import *
import vision.threshold

class OpenCVPitch(Capture):

    def __init__(self, filename=None, once=False):
        Capture.__init__(self, Vision.rawSize, filename, once)
        self.tmpfile = tempfile.mktemp(suffix='.bmp')
        self.threshold = vision.threshold.PrimaryRaw
        self.pre = Preprocessor(Vision.rawSize, self.threshold)

    def __del__(self):
        os.remove(self.tmpfile)

    def get(self):
        frame = self.getFrame()

        # Remove distortions from the raw image
        frame = self.pre.standardise(frame)

        cv.SaveImage(self.tmpfile, frame)
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


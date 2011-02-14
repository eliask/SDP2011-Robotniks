from glob import glob
import cv, os, sys, logging
from common.world import World
from vision.vision import Vision
import unittest2 as unittest

class TestContinuous(unittest.TestCase):
    """Run tests using recorded video

    TODO: currently the tests will never fail. To fix this, the world
    state needs to be analysed, and be subject to some threshold like
    "all entities must be recognised at least 90% of the time".
    """

    base = 'test/vision/'
    def setUp(self):
        self.log = logging.getLogger("test.vision.continuous")

    def test_continuous_recog_prim1(self):
        video = self.base+'prim1.mpg'
        world = World('blue') #arbitrary colour

        v = Vision(world, video, once=True, headless=True)
        # Skip a numbe of frames waiting for the image to stabilise:
        v.run(skip=20, until=60)

    def test_continuous_recog_prim2(self):
        video = self.base+'prim2.mpg'
        world = World('blue')

        v = Vision(world, video, once=True, headless=True)
        v.run(until=50)

    def test_continuous_recog_alt1(self):
        video = self.base+'alt1.mpg'
        world = World('blue')

        v = Vision(world, video, once=True, headless=True)
        v.run(until=50)

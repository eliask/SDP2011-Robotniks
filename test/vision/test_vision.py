from glob import glob
import cv, os, sys, logging
import vision.threshold
from vision.preprocess import Preprocessor
from vision.features import FeatureExtraction
import unittest2 as unittest

class TestVision(unittest.TestCase):
    base = 'test/vision/'

    def setUp(self):
        self.threshold = vision.threshold.AltRaw()
        self.log = logging.getLogger("test.vision")

    def test_recognition(self):
        N = 0
        balls = glob(self.base+'ball*.png')
        for ball in balls:
            image = cv.LoadImage(ball)
            ents = self.recognise(image)
            if len(ents['balls']) == 1:
                N += 1
            else:
                self.log.warn("Failed to recognise (just) one ball in: %s", ball)

        self.assertEqual( N, len(balls), 'Imperfect ball recognition' )

    def test_dirmarker_recog(self):
        dirmarkers = glob(self.base+'dirmarker*.png')
        N = 0
        for dirmarker in dirmarkers:
            image = cv.LoadImage(dirmarker)
            if self.recogniseDirmarker(image):
                N += 1
            else:
                self.log.warn("Failed to recognise a dirmarker in %s:", dirmarker)

        self.assertEqual( N, len(dirmarkers), 'Imperfect dirmarker recognition' )

    def test_yellow_recog(self):
        robots = glob(self.base+'yellow*.png')
        N = 0
        for yellow in robots:
            image = cv.LoadImage(yellow)
            ents = self.recognise(image)
            if ents['yellow']: #and ents['yellow']['T']:
                N += 1
            else:
                self.log.warn("Failed to recognise a yellow T in: %s", yellow)

        self.assertEqual( N, len(robots), 'Imperfect yellow T recognition' )

    def test_blue_recog(self):
        robots = glob(self.base+'blue*.png')
        N = 0
        for blue in robots:
            image = cv.LoadImage(blue)
            ents = self.recognise(image)
            if ents['blue']: # and ents['blue']['T']:
                N += 1
            else:
                self.log.warn("Failed to recognise a blue T in: %s", blue)

        self.assertEqual( N, len(robots), 'Imperfect blue T recognition' )

    def recogniseDirmarker(self, image):
        size = (image.width, image.height)
        # A dummy robot that would have been used for testing whether
        # the dirmarker was inside the robot:
        dummy = {'box':((int(size[0]/2.0), int(size[1]/2.0)), size, 0)}

        featureEx = FeatureExtraction(size, self.threshold)
        ents = featureEx.detectDirMarker(dummy, image)
        return ents

    def recognise(self, image):
        size = (image.width, image.height)
        pre = Preprocessor(size, self.threshold, None, True)
        featureEx = FeatureExtraction(size)

        bgsub, mask = pre.bgsub(image)
        ents = featureEx.features(bgsub, self.threshold)

        return ents


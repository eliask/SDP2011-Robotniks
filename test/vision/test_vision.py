from glob import glob
import cv, os, sys, logging
import vision.threshold
from vision.preprocess import Preprocessor
from vision.features import FeatureExtraction
import unittest2 as unittest

class TestVision(unittest.TestCase):
    """Test image-based object recognition

    Currently this is very much coupled with the other vision test,
    even though neither this nor that test case explicitly mention
    each other. The reason for this is that the histogram adjustment
    modifies the "global" threshold values, and those values end up
    being used here. This actually slightly improves the performance
    of detecting the blue T, but completely breaks direction marker
    detection.
    """

    base = 'test/vision/'

    def setUp(self):
        self.threshold = vision.threshold.AltRaw()
        self.log = logging.getLogger("test.vision.static")

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

    def test_global_recog(self):
        "Test full scene recognition"
        images = glob(self.base+'global*.png')
        N = 0
        for image in images:
            im = cv.LoadImage(image)
            size = (im.width, im.height)
            print size
            pre = Preprocessor(size, self.threshold)
            featureEx = FeatureExtraction(pre.cropSize)

            standard = pre.get_standard_form(im)
            bgsub, mask = pre.bgsub(standard)

            ents = featureEx.features(bgsub, self.threshold)
            if not ents['blue']:
                self.log.warn("Failed to recognise the blue robot in: %s", image)
            if not ents['yellow']:
                self.log.warn("Failed to recognise the yellow robot in: %s", image)
            if not ents['balls']:
                self.log.warn("Failed to recognise the ball in: %s", image)
            if len(ents['balls']) > 1:
                self.log.warn("Recognised more than one ball in: %s", image)

            if ents['blue'] and ents['yellow'] and ents['balls']:
                N += 1

        self.assertEqual( N, len(images), 'Imperfect global scene recognition' )

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


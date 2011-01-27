import cv
import logging

class CaptureFailure(Exception): pass

class Capture:

    def __init__(self, size, filename=None, once=False):
        self.size = size
        self.once = once
        self.filename = filename
        self.initCapture()

    def initCapture(self):
        if self.filename:
            logging.info("Capturing from file: %s", self.filename)
            self.capture = cv.CaptureFromFile(self.filename)
        else:
            logging.info("Capturing from camera")
            self.capture = cv.CaptureFromCAM(-1)

        if not self.capture:
            raise CaptureFailure, "Could not open video capture stream"

        cv.SetCaptureProperty(self.capture,
                              cv.CV_CAP_PROP_FRAME_WIDTH,
                              self.size[0])
        cv.SetCaptureProperty(self.capture,
                              cv.CV_CAP_PROP_FRAME_HEIGHT,
                              self.size[1])

    def __getFrame(self):
        """Returns a new frame from the video stream in BGR format

        Raises an exception if there is an error acquiring a frame.
        """
        frame = cv.QueryFrame(self.capture)
        if frame is None:
            raise CaptureFailure

        assert frame.width == self.size[0] \
            and frame.height == self.size[1], \
            "Video dimensions don't match configured resolution"

        return frame

    def getFrame(self):
        try:
            frame = self.__getFrame()
        except CaptureFailure:
            logging.info("No more frames from the capture device")
            if self.once: raise
            logging.info("Attempting to re-initialise video capture:")
            self.initCapture()
            frame = self.__getFrame()
        return frame

from opencv import cv, highgui
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
            logging.info("Capturing from file: %s" % self.filename)
            self.capture = highgui.cvCreateFileCapture(self.filename)
        else:
            logging.info("Capturing from camera")
            # First assume the camera is a v4L2 one
            self.capture = highgui.cvCreateCameraCapture(highgui.CV_CAP_V4L2)
            if not self.capture:
                # If not, open a window for choosing between all other cameras
                self.capture = highgui.cvCreateCameraCapture(-1)

        if not self.capture:
            raise CaptureFailure, "Could not open video capture stream"

        highgui.cvSetCaptureProperty(self.capture,
                                     highgui.CV_CAP_PROP_FRAME_WIDTH,
                                     self.size.width)
        highgui.cvSetCaptureProperty(self.capture,
                                     highgui.CV_CAP_PROP_FRAME_HEIGHT,
                                     self.size.width)

    def __del__(self):
        highgui.cvReleaseCapture(self.capture)

    def __getFrame(self):
        """Returns a new frame from the video stream in BGR format

        Raises an exception if there is an error acquiring a frame.
        """
        frame = highgui.cvQueryFrame(self.capture)
        if frame is None:
            raise CaptureFailure

        assert frame.width == self.size.width
        assert frame.height == self.size.height
        return frame

    def getFrame(self):
        try:
            frame = self.__getFrame()
        except CaptureFailure:
            if self.once: raise
            self.initCapture()
            frame = self.__getFrame()
        return frame

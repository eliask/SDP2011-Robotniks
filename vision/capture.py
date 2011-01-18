from opencv import cv, highgui

class CaptureFailure(Exception): pass

class Capture:

    def __init__(self, size, filename=None):
        if filename:
            self.capture = highgui.cvCreateFileCapture(filename)
        else:
            # First assume the camera is a v4L2 one
            self.capture = highgui.cvCreateCameraCapture(highgui.CV_CAP_V4L2)
            if not self.capture:
                # If not, open a window for choosing between all other cameras
                self.capture = highgui.cvCreateCameraCapture(-1)

        if not self.capture:
            raise CaptureFailure, "Could not open video capture stream"

        highgui.cvSetCaptureProperty(self.capture,
                                     highgui.CV_CAP_PROP_FRAME_WIDTH,
                                     size.width)
        highgui.cvSetCaptureProperty(self.capture,
                                     highgui.CV_CAP_PROP_FRAME_HEIGHT,
                                     size.width)

    def __del__(self):
        highgui.cvReleaseCapture(self.capture)

    def getFrame(self):
        """Returns a new frame from the video stream in BGR format

        Raises an exception if there is an error acquiring a frame.
        """
        frame = highgui.cvQueryFrame(self.capture)
        if frame is None:
            raise CaptureFailure

        return frame

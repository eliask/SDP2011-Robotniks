from opencv import cv, highgui
import logging

class CaptureFailure(Exception): pass

class Capture:

    def __init__(self, size, filename=None):
        self.size = size
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

    def getFrame(self):
        """Returns a new frame from the video stream in BGR format

        Raises an exception if there is an error acquiring a frame.
        """
        frame = highgui.cvQueryFrame(self.capture)
        if frame is None:
            raise CaptureFailure

        assert frame.width == self.size.width
        assert frame.height == self.size.height
        return frame


# GL_CAPS = "video/x-raw-rgb,width=%d,pixel-aspect-ratio=1/1,red_mask=(int)0xff0000,green_mask=(int)0x00ff00,blue_mask=(int)0x0000ff" % size[0]
# pipeline = gst.parse_launch("%s ! ffmpegcolorspace ! appsink name=camera_sink emit-signals=True caps=%s" % ("v4l2src", GL_CAPS))
# camera_sink = pipeline.get_by_name('camera_sink')
# p = pipeline.set_state(gst.STATE_PLAYING)
# c = camera_sink.emit('pull-buffer')
#frame = 

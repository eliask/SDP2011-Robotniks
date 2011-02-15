import cv
import logging, os
from subprocess import Popen

class MPlayerCapture:

    def __init__(self, size, filename=None, once=False):
        self.size = size
        self.once = once
        self.filename = filename
        self.cur_frame = 2
        self.dir = self.getStoreDir()

    def getStoreDir(self):
        return open('.mplayer-store', 'r').readline().strip()

    def getName(self, num):
        return '%s/%08d.png' % (self.dir, num)

    def fileExists(self, num):
        try:
            h = open(self.getName(num), 'r')
            #print len(h.readline())
            h.close()
            return True
        except IOError:
            return False

    def __getFrame(self):
        """Returns a new frame from the video stream in BGR format

        Raises an exception if there is an error acquiring a frame.
        """

        while True:
            if self.fileExists(self.cur_frame+1):
                os.remove( self.getName(self.cur_frame-1) )
                self.cur_frame += 1
            elif self.fileExists(self.cur_frame):
                # Use the /second latest/ image to work around mplayer
                # sometimes having a write lock of sorts on the file.
                frame = cv.LoadImage( self.getName(self.cur_frame-1) )
                break

        assert frame.width == self.size[0] \
            and frame.height == self.size[1], \
            "Video dimensions don't match configured resolution"

        return frame

    def getFrame(self):
        return self.__getFrame()


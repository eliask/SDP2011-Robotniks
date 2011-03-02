import cv
import logging
import os
import os.path
import subprocess

"""
Files with these extensions will be treated as images and loaded as such.
"""
IMAGE_EXTS = ["png", "jpg", "jpeg"]

"""
The Capture class handles quiring frames from a given input.
"""
class Capture:
	"""
	Sets up the class with desired parameters.

	size: The expected size of the input frames
	filename: (Optional) the path to a file (image/video) to use for frame(s)
	once: (Optional) when True, a video input will only run once
	"""
	def __init__(self, size, files=[], once = False):
		self.size = size
		self.files = files
		self.once = once
		self.initCapture()

	def initCapture(self):
                """
                Initialises the capture source.
                """
		self.capture = None
		self.image = None

		if self.files:
                        filename = self.files.pop()
                        self.files.insert(0, filename)
			logging.info("Capturing from file: %s" % filename)

			if filename.split(".")[-1] in IMAGE_EXTS:
				self.image = cv.LoadImage(filename)
                                self.image_used = False
			else:
				self.capture = cv.CaptureFromFile(filename)
		else:
			logging.info("Capturing from camera")
			self.initMPlayer()

	"""
	Initialises MPlayer.  This is required to work around the interlaced feed
	that cv.CaptureFromCAM() cannot deal with.

	TODO: actually start MPlayer inside the script so it doesn't
	need to be started manually
	"""
	def initMPlayer(self):
                assert os.environ['MPLAYER_CAPTURE'], \
                    'The environment variable MPLAYER_CAPTURE must be set'
		self.mplayer = bool(int(os.environ['MPLAYER_CAPTURE']))

		logging.info("Starting MPlayer")
		self.cur_frame = 2
		self.dir = open('.mplayer-store', 'r').readline().strip()

	def getMPlayerFrame(self):
		def getName(num):
			return '%s/%08d.jpg' % (self.dir, num)

		def frameExists(num):
			try:
				h = open(getName(num), 'r')
				h.close()
				return True
			except IOError:
				return False

		logging.debug("Getting MPlayer frame %d" % self.cur_frame)

		while True:
			if frameExists(self.cur_frame + 1):
				os.remove(getName(self.cur_frame - 1))
				self.cur_frame += 1
			elif frameExists(self.cur_frame):
				frame = cv.LoadImage(getName(self.cur_frame - 1))
				break
                        elif len( os.listdir(".") ) > 0:
                                self.cur_frame += 1

		return frame

	"""
	Internal function to aquire a frame from the source.  Throws an exception
	if the input is exhausted.  Resulting image is in BGR format.
	"""
	def __getFrame(self):
		if self.image:
                        if self.image_used:
                                raise EOF
			logging.info("Getting frame from image")
			frame = cv.CloneImage(self.image)
                        self.image_used = True
		elif self.capture:
			logging.info("Getting frame from OpenCV capture")
			frame = cv.QueryFrame(self.capture)
		else:
			logging.info("Getting frame from MPlayer")
			frame = self.getMPlayerFrame()

		if not frame:
			raise EOF

		assert frame.width == self.size[0] and frame.height == self.size[1],\
                    "Aquired frame does not match expected input size."

		return frame

	"""
	External access point to get a frame.  Will attempt to re-initialise the input
	on CaptureFailure (given that once is False).
	"""
	def getFrame(self):
		try:
			frame = self.__getFrame()
		except EOF:
			logging.info("No more frames available from input.")

			if self.once:
				raise

			logging.info("Attempting to re initialise input.")
			self.initCapture()
			frame = self.__getFrame()

		return frame

"""
Stub exception thrown on capture exhaustion.
"""
class EOF(Exception):
	pass

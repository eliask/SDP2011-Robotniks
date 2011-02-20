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
	def __init__(self, size, filename = None, once = False):
		self.size = size
		self.filename = filename
		self.once = once
		self.initCapture()
	
	"""
	Initialises the capture source.
	"""
	def initCapture(self):
		self.capture = None
		self.image = None
		self.mplayer = False
		
		if self.filename:
			logging.info("Capturing from file: %s" % self.filename)
			
			if self.filename.split(".")[-1] in IMAGE_EXTS:
				self.capture = True
				self.image = cv.LoadImage(self.filename)
			else:
				self.capture = cv.CaptureFromFile(self.filename)
		else:
			logging.info("Capturing from camera")
			self.mplayer = True
			self.initMPlayer()
	
	"""
	Initialises MPlayer.  This is required to work around the interlaced feed
	that cv.CaptureFromCAM() cannot deal with.
	
	TODO: actually start MPlayer inside the script so it doesn't need to be started manually
	"""
	def initMPlayer(self):
		logging.info("Starting MPlayer")
		#args = ["./start-mplayer.sh"]
		#subprocess.Popen(args)#, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		self.cur_frame = 2
		self.dir = open('.mplayer-store', 'r').readline().strip()
	
	"""
	Gets a frame from the mplayer cache.
	"""
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

		return frame
	
	"""
	Internal function to aquire a frame from the source.  Throws an exception
	if the input is exhausted.  Resulting image is in BGR format.
	"""
	def __getFrame(self):
		if self.image:
			logging.info("Getting frame from image")
			frame = cv.CloneImage(self.image)
		elif self.mplayer:
			logging.info("Getting frame from MPlayer")
			frame = self.getMPlayerFrame()
		else:
			logging.info("Getting frame from capture")
			frame = cv.QueryFrame(self.capture)
		
		if not frame:
			raise EndOfCapture
		
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
		except EndOfCapture:
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
class EndOfCapture(Exception):
	pass

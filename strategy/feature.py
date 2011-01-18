import geometry

# The feature class is the base class representing a robot or the ball.
class Feature(object):
	# Initalises the feature.
	def __init__(self, x, y, orientation, length, width, previous):
		self.x = x
		self.y = y
		self.orientation = orientation
		self.length = length
		self.width = width
		self.velocity = geometry.euclidean_distance(self.position(), previous.position()) / State.time_since_previous()

import geometry

# The feature class is the base class representing a robot or the ball.
class Feature(object):
	# Initalises the feature.
	def __init__(self, data):
		self.x = data['x']
		self.y = data['y']
		self.orientation = data['orientation']
		self.length = data['length']
		self.width = data['width']
	
	# Checks is this feature is next to another.
	def isNextTo(feature):
		# Check if the distance between the features is within a 'next to' threshold
		if(geometry.euclideanDistance([self.x, self.y], [feature.x, feature.y]) < 1):
			return True
		else
			return False

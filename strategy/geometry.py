# The geometry class provides useful geometry functions.
class Geometry(object):
	# Calculates the euclidean distance between two points.
	def euclidean_distance(point1, point2):
		return sqrt(((point1[0] - point2[0]) ** 2) + ((point1[1] - point2[1]) ** 2))

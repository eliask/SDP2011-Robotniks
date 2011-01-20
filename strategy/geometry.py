# The geometry module provides useful geometry functions.

# Calculates the euclidean distance between two points.
def euclideanDistance(point1, point2):
	return sqrt(((point1[0] - point2[0]) ** 2) + ((point1[1] - point2[1]) ** 2))

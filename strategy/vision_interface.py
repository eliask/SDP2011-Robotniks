# The VisionInterface class provides the interface for retriving vision data.
class VisionInterface(object):
	def get_data():
		return {
			'us': {
				'x': 0, 'y': 0, 'orientation': 0, 'length': 0, 'width': 0
			},
			'them': {
				'x': 0, 'y': 0, 'orientation': 0, 'length': 0, 'width': 0
			},
			'ball': {
				'x': 0, 'y': 0, 'orientation': 0, 'length': 0, 'width': 0
			}}

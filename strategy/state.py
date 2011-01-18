import time
import geometry

# The State class represents a state of the field.
class State(object):
	
	
	# Initialises a new state.
	def __init__(self, vision_data, previous_state):
		self.time = time.time()
		
		self.us = Robot(
			vision_data['us']['x'],
			vision_data['us']['y'],
			vision_data['us']['orientation'],
			vision_data['us']['length'],
			vision_data['us']['width'],
			previous_state.us
		)
		
		self.them = Robot(
			vision_data['them']['x'],
			vision_data['them']['y'],
			vision_data['them']['orientation'],
			vision_data['them']['length'],
			vision_data['them']['width'],
			previous_state.them
		)
		
		self.them = Ball(
			vision_data['ball']['x'],
			vision_data['ball']['y'],
			vision_data['ball']['orientation'],
			vision_data['ball']['length'],
			vision_data['ball']['width'],
			previous_state.ball
		)

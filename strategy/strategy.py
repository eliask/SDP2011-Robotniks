# Handles the generation of a strategy.
class Strategy(object):
	# Update the current state.
	def updateState():
		data = VisionInterface.getData()
		self.us = Robot(data['us'])
		self.them = Robot(data['them'])
		self.ball = Robot(data['ball'])	
	
	# Generate the strategy.
	def doStrategy():
		self.updateState()
		sendCommand('kick')
	
	def sendCommand(command):
		RobotInterface.sendCommand(command)

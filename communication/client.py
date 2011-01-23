import socket

class Client:

	def __init__(self):
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client_socket.connect(("localhost", 6879))

	def sendMessage(self, x):
		self.client_socket.send(str(x))

	def reset(self):
		self.sendMessage(0)

	def drive(self):
		self.sendMessage(1)

	def stop(self):
		self.sendMessage(2)

	def startSpinRight(self):
		self.sendMessage(3)

	def startSpinLeft(self):
		self.sendMessage(4)

	def stopSpin(self):
		self.sendMessage(5)

	def setRobotDirection(self, angle):
		self.sendMessage(angle - 6)

	def kick(self):
		self.sendMessage(366)

	def spinRightShort(self):
		self.sendMessage(367)

	def spinLeftShort(self):
		self.sendMessage(368)


	

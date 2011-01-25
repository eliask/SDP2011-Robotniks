import socket
import interface

class RealRobotInterface(interface.RobotInterface):

	def __init__(self):
		self.client_socket = \
                    socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client_socket.connect(("localhost", 6879))

	def sendMessage(self, x):
		self.client_socket.send('%d\n' % x)

	def reset(self):
		self.sendMessage(100)
	def drive(self):
		self.sendMessage(101)
	def stop(self):
		self.sendMessage(102)
	def startSpinRight(self):
		self.sendMessage(103)
	def startSpinLeft(self):
		self.sendMessage(104)
	def stopSpin(self):
		self.sendMessage(105)
	def setRobotDirection(self, angle):
                "Turn the specified angle in radians"

                # The robot takes in a clockwise integer angle in degrees
                angle = int(round(degrees(angle))) % 360
                if angle < 180:
                        angle = angle + 180
                else:
                        angle = angle - 180

                msg = 6 + angle
                assert 6 <= msg <= 365
                self.sendMessage(msg)

	def kick(self):
		self.sendMessage(466)
	def spinRightShort(self):
		self.sendMessage(467)
	def spinLeftShort(self):
		self.sendMessage(468)


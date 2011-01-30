import interface
import socket
import logging
import time

class RealRobotInterface(interface.RobotInterface):

	def __init__(self):
		logging.info("Physical robot interface started")
		self.client_socket = \
                    socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client_socket.connect(("localhost", 6879))
		logging.info("Connected to robot interface server")

	def sendMessage(self, x):
		logging.debug("Told the robot: %d", x)
		self.client_socket.send('%d\n' % x)
		time.sleep(0.5)

	def reset(self):
		self.sendMessage(100)

	def drive(self):
		print ("Sent command: drive")
		self.sendMessage(101)
	def stop(self):
		self.sendMessage(102)
	def startSpinRight(self):
		print ("Sent command: spin right")
		self.sendMessage(103)
	def startSpinLeft(self):
		print ("Sent command: spin left")
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
                assert 106 <= msg <= 465
                self.sendMessage(msg)

	def kick(self):
		self.sendMessage(466)
	def spinRightShort(self):
		self.sendMessage(467)
	def spinLeftShort(self):
		self.sendMessage(468)

	def shutdownServer(self):
		self.sendMessage(-1)



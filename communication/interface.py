import PCBluetooth as BT
from math import *

class Interface(BT):
    def init(self):
        self.openConnection();

    def reset(self):
        self.sendMessage(0)
    def drive(self):
        self.sendMessage(1)
    def stop(self):
        self.sendMessage(2)
    def startSpinLeft(self):
        self.sendMessage(3)
    def startSpinRight(self):
        self.sendMessage(4)
    def stopSpin(self):
        self.sendMessage(5)
    def turnAngle(self, angle):
        "Turn the specified angle in radians"

        # The robot takes in a clockwise integer angle in degrees
        angle = int(round(degrees(angle))) % 360
        if angle < 180:
            angle = angle + 180
        else:
            angle = angle - 180

        msg = 6 + angle
        assert 6 < msg < 365
        self.sendMessage(msg)

    def kick(self):
        self.sendMessage(366)

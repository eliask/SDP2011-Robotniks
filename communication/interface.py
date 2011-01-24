
class RobotInterface(object):
    "The abstract base class for interfacing with the robot"
    def tick(self):
        """Perform communication interface state update.

        This is for doing any periodic "house-keeping" stuff like
        updating the simulator robot object.
        """
        pass

    def reset(self): pass
    def drive(self): pass
    def stop(self): pass
    def startSpinRight(self): pass
    def startSpinLeft(self): pass
    def stopSpin(self): pass
    def setRobotDirection(self, angle): pass
    def kick(self): pass
    def spinRightShort(self): pass
    def spinLeftShort(self): pass


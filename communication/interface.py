import time
import logging
from math import *

REPLAY_LOG_DIRECTORY = "logs/communication/replay/"

class RobotInterface(object):
    """The base class for interfacing with the robot.

    Currently the base class exists to provide an interface for any
    robot interfaces, and to record all commands sent to the robot.
    """

    def __init__(self, log=True):
        # Set up the replay logger.
        self.start_time = time.time()
        if log:
            self.replay_logger = logging.getLogger('replay_logger')
            self.replay_logger.setLevel(logging.DEBUG)
            handler = logging.FileHandler(REPLAY_LOG_DIRECTORY + \
                time.strftime("%Y%m%d-%H%M%S", \
                time.localtime(self.start_time)), "w")
            self.replay_logger.addHandler(handler)
        else:
            self.replay_logger = None

        self.initCommands()

    def recordCommands(self):
        time_since_init = time.time() - self.start_time
        command_string = "%d,%d,%d,%d,%d,%d" \
            % ( int(self._reset), int(self._kick),
                self._drive_left, self._drive_right,
                self._steer_left, self._steer_right )

        if self.replay_logger:
            self.replay_logger.debug(
                "%.3f\t%s" % (time_since_init, command_string) )

    def initCommands(self):
        "Resets the commands to the defaults."
        self._reset = False
        self._kick  = False
        self._drive_left = 0
        self._drive_right = 0
        self._steer_left = 0
        self._steer_right = 0

    def tick(self):
        """Perform communication interface state update.

        This is for doing any periodic "house-keeping" stuff like
        updating the simulator robot object.
        """
        self.recordCommands()

    def drive_both(self, setting):
        self.drive_left(setting)
        self.drive_right(setting)

    def steer_both(self, angle):
        self.steer_left(angle)
        self.steer_right(angle)

    def steer_left_incr(self, angle):
        "A helper function for the UI _only_"
        delta = radians(angle) + self.steer_left_target
        if self.steer_left_until < time.time():
            self.steer_left_until = time.time() + 0.6
            self.steer_left(delta)
    def steer_right_incr(self, angle):
        "A helper function for the UI _only_"
        delta = radians(angle) + self.steer_right_target
        if self.steer_right_until < time.time():
            self.steer_right_until = time.time() + 0.6
            self.steer_right(delta)

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


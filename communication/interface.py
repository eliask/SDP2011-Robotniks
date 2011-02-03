import time
import logging

REPLAY_LOG_DIRECTORY = "logs/communication/replay/"

class RobotInterface(object):
    """The base class for interfacing with the robot.

    Currently the base class exists to provide an interface for any
    robot interfaces, and to record all commands sent to the robot.
    """

    def __init__(self):
        # Set up the replay logger.
        self.start_time = time.time()
        self.replay_logger = logging.getLogger('replay_logger')
        self.replay_logger.setLevel(logging.DEBUG)

        handler = logging.FileHandler(REPLAY_LOG_DIRECTORY +
            time.strftime("%Y%m%d-%H%M%S", time.localtime(self.start_time)), "w")
        self.replay_logger.addHandler(handler)

    def recordCommands(self):
        time_since_init = time.time() - self.start_time
        command_string = "%d,%d,%d,%d,%d,%d" \
            % ( int(self.reset), int(self.kick),
                self.drive1, self.drive2, self.turn1, self.turn2 )
        self.replay_logger.info( "%.3f\t%s" % (time_since_init, command_string) )

    def initCommands(self):
        "Resets the commands to the defaults."
        self.reset = False
        self.kick  = False
        self.drive1 = 0
        self.drive2 = 0
        self.turn1 = 0
        self.turn2 = 0

    def tick(self):
        """Perform communication interface state update.

        This is for doing any periodic "house-keeping" stuff like
        updating the simulator robot object.
        """
        self.recordCommands()

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


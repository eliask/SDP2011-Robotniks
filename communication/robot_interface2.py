import interface
import socket
import logging
from datetime import datetime

REPLAY_LOG_DIRECTORY = "logs/communication/replay/"

class RealRobotInterface(interface.RobotInterface):
    
    """
    Number of speed settings for each direction.  Zero is counted twice.
    """
    MotorPrecision = 4
    
    """
    Initialises the RealRobotInterface.
    """
    def __init__(self):
        logging.info("Physical robot interface 2 started")
        self.client_socket = \
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("localhost", 6879))
        logging.info("Connected to robot interface server")
        
        # Set up the replay logger.
        self.init_time = datetime.now()
        self.replay_logger = logging.getLogger('replay_logger')
        self.replay_logger.setLevel(logging.DEBUG)
        
        handler = logging.FileHandler(REPLAY_LOG_DIRECTORY + 
            self.init_time.strftime("%d-%m-%y %H-%M-%S"), "w")
        self.replay_logger.addHandler(handler)
    
    """
    Resets the commands to the defaults.
    """
    def initCommands(self):
        self.reset = False
        self.kick  = False
        self.drive1 = 0
        self.drive2 = 0
        self.turn1 = 0
        self.turn2 = 0
    
    """
    Logs all the commands in a message."
    """
    def logCommands(self):
        Prec = self.MotorPrecision
        logging.info( "Sent the robot the command:" )
        logging.info( "reset: %d" % int(self.reset) )
        logging.info( "kick: %d" % int(self.kick) )
        logging.info( "drive1: %c%d" %
                      {True:' Fwd',False:'Back'}[self.drive1&Prec > 0],
                      self.drive1 & (Prec-1) )
        logging.info( "drive2: %c%d" %
                      {True:' Fwd',False:'Back'}[self.drive2&Prec > 0],
                      self.drive2 & (Prec-1) )
        logging.info( "turn1: %c%d" %
                      {True:'CCW',False:' CW'}[self.turn1&Prec > 0],
                      self.turn1 & (Prec-1) )
        logging.info( "turn2: %c%d" %
                      {True:'CCW',False:' CW'}[self.turn2&Prec > 0],
                      self.turn2 & (Prec-1) )
    
    """
    Logs a message to the replay logfile for later playback.
    """
    def logMessage(self, message):
        time_since_init = int(datetime.now().strftime("%s")) - \
            int(self.init_time.strftime("%s"))
        self.replay_logger.info( "%d %d" % (time_since_init, message))
    
    """
    Encodes the current commands into a transmitable message.
    """
    def encodeCommands(self):
        """
        The binary command encoding:
        0      1     001     100   111    010     10
        ^      ^     ^        ^     ^      ^       ^
        |     kick   |        |   Turn     |  Two unused bits
        don't    Move wheel1  |  wheel1 CW |    out of 16
        reset      forward    | at speed 3 |
                  at speed 1  |            |
                        Stop/don't move    |
                            wheel2         |
                                     Turn wheel2 CCW
                                       at speed 2

        Note that the encoding has the property the the "stop
        everything" command is encoded simply as 0.

        reset = reset wheel positions if 1.
        kick =  start kick if 1.

        General steering commands for the 4 motors:
        Note: X means "don't care" or "either 1 or 0"
        for motor commands, X00 means stop;
        0XX is for going forward at setting XX,
        1XX is for going forward at setting XX,

        Example: 010 is to go forward at speed setting 2/3
                 111 is to go backward at speed setting 3/3
                 100 and 000 both stop the robot.

        Turning motors take as input the same commands, and
        "forward" is interpreted as going counter-clockwise.
        """
        message = 0L

        message &= self.reset << 0
        message &= self.kick << 1
        message &= self.motor1_dir << 2
        message &= self.motor2_dir << 5
        message &= self.turn1 << 8
        message &= self.turn2 << 11

        return message
    
    """
    Sends the current commands, as a message, to the robot.
    """
    def sendMessage(self, x):
        message = self.encodeCommands()
        logging.debug("Told the robot: %d", x)
        self.client_socket.send('%d\n' % x)
        self.initCommands()
    
    """
    Sets the reset command to be sent.
    """
    def reset(self):
        self.reset = True
    
    """
    Calculates the appropriate value for a drive command given the speed
    setting.
    """
    def __drive(self, setting):
        Prec = self.MotorPrecision
        return int(setting < 0)*Prec & (setting & (Prec-1))
    
    """
    Sets the drive1 command to be sent with given speed setting.
    """
    def drive1(self, setting):
        self.drive1 = self.__drive(setting)
    
    """
    Sets the drive2 command to be sent with given speed setting.
    """
    def drive2(self, setting):
        self.drive2 = self.__drive(setting)
    
    """
    Sets the turn1 command to be sent with given speed setting.
    """
    def turn1(self, setting):
        self.turn1 = self.__drive(setting)
    
    """
    Sets the drive2 command to be sent with given speed setting.
    """
    def turn2(self, setting):
        self.turn2 = self.__drive(setting)
    
    """
    Sends the shutdown signal to the robot and closes the socket.
    """
    def shutdownServer(self):
        self.sendMessage(-1)
        self.client_socket.close()

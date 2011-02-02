import interface
import socket
import logging
import time

class RealRobotInterface(interface.RobotInterface):

    MotorPrecision = 4 # number of speed settings for each direction.
                       # Zero is counted twice.

    def __init__(self):
        logging.info("Physical robot interface 2 started")
        self.client_socket = \
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("localhost", 6879))
        logging.info("Connected to robot interface server")

    def initCommands(self):
        self.reset = False
        self.kick  = False
        self.drive1 = 0
        self.drive2 = 0
        self.turn1 = 0
        self.turn2 = 0

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

    def sendMessage(self, x):
        message = self.encodeCommands()
        logging.debug("Told the robot: %d", x)
        self.client_socket.send('%d\n' % x)
        self.initCommands()

    def reset(self):
        self.reset = True

    def __drive(self, setting):
        Prec = self.MotorPrecision
        return int(setting < 0)*Prec & (setting & (Prec-1))

    def drive1(self, setting):
        self.drive1 = self.__drive(setting)
    def drive2(self, setting):
        self.drive2 = self.__drive(setting)
    def turn1(self, setting):
        self.turn1 = self.__drive(setting)
    def turn2(self, setting):
        self.turn2 = self.__drive(setting)

    def shutdownServer(self):
        self.sendMessage(-1)



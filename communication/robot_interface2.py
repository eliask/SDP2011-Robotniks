import interface
import socket
import logging

class RealRobotInterface(interface.RobotInterface):

    # Number of speed settings for each direction. Zero is counted twice.
    MotorPrecision = 4
    SteerPrecision = 1<<9

    def __init__(self):
        super(RealRobotInterface, self).__init__()
        logging.info("Physical robot interface 2 started")
        self.client_socket = \
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("localhost", 6879))
        logging.info("Connected to robot interface server")

    def humanLogCommands(self):
        "Log commands in a (perhaps) more human-readable way"
        logging.info( "Sent the robot the command:" )

        logging.info( "reset: %d" % int(self._reset) )
        logging.info( "kick: %d" % int(self._kick) )

        Prec = self.MotorPrecision
        logging.info( "drive_left: %d %s" %
                      ( self._drive_left & (Prec-1),
                        {True:' Fwd',False:'Back'}[self._drive_left&Prec > 0] ))
        logging.info( "drive_right: %d %s" %
                      ( self._drive_right & (Prec-1),
                        {True:' Fwd',False:'Back'}[self._drive_right&Prec > 0] ))

        logging.info( "steer_left: %d" % self._steer_left )
        logging.info( "steer_right: %d" % self._steer_right )

    def encodeCommands(self):
        "Encodes commands into a message for transmission."
        message = 0L

        message |= self._reset << 0
        message |= self._kick << 1
        message |= self._drive_left << 2
        message |= self._drive_right << 5
        message |= self._steer_left << 8
        message |= self._steer_right << 17

        return message

    def sendMessage(self):
        "Sends the current commands to the robot."
        self.tick()
        message = self.encodeCommands()
        self.humanLogCommands()
        self.client_socket.send('%d\n' % message)
        self.initCommands()

    def reset(self):
        self._kick = True

    def reset(self):
        self._reset = True

    def __drive(self, setting):
        """
        Calculates the appropriate value for a drive command given the
        speed setting.
        """
        Prec = self.MotorPrecision
        return int(setting < 0)*Prec | (setting & (Prec-1))

    def drive(self, setting):
        """
        Drive forward using both wheels--more flexible control has not
        yet been implemented.
        """
        self._drive_right = self.__drive(setting)

    def drive_left(self, setting):
        self._drive_left = self.__drive(setting)

    def drive_right(self, setting):
        self._drive_right = self.__drive(setting)

    def __steer(self, _angle):
        """
        Calculates the appropriate value for a drive command given the
        speed setting.
        """
        Prec = self.SteerPrecision
        angle = int(degrees(_angle)) % 360
        return (angle & (Prec-1))

    def steer_left(self, angle):
        "Steer the left wheel to this absolute position, in radians"
        self._steer_left = self.__steer(angle)

    def steer_right(self, angle):
        "Steer the right wheel to this absolute position, in radians"
        self._steer_right = self.__steer(angle)

    def shutdownServer(self):
        """
        Sends the shutdown signal to the robot and closes the socket.
        """
        self.sendMessage(-1)
        self.client_socket.close()

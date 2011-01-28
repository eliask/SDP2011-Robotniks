from communication.interface import *
import numpy as np
from math import *
import logging

class SimRobotInterface(RobotInterface):
    """The simulated robot interface for updating the physical
    parameters parameters of the robot.

    We only keep track of the measures that are necessary to update
    the state of the robot, but not the absolute state, since that is
    contingent on the initial state. Hence we don't track the position
    here.

    We also don't track the orientation, since the robot movement
    itself is symmetric (we can assume as an approximation), and
    basically only the kicker and the collision detection require
    knowing where we are "heading".
    """

    def __init__(self, *args):
        RobotInterface.__init__(self, *args)

        self.v = np.array([0.0, 0.0])
        self.accel = 0

        self.ang_v = 0
        self.ang_accel = 0
        self.rotAngle = 0
        self.maxSpeed = 6

        self.movement_dir = 0       # The direction the wheels point at
        self.movement_dir_speed = 0 # The speed at which the wheels turn

    def cooldown(self, secs):
        """Wait the specified amount of seconds until the next command
        is possible.
        """
        pass

    def reset(self):
        """Puts the robot's wheels in their default setting of 0 Deg

        The direction is relative to the robot's orientation.
        """
        # TODO: make this take time, like acceleration
	self.movement_dir = self.orientation
        self.cooldown(0.5)

    def drive(self):
        "Drive the motors forwards"
        # TODO: trade off between the two
        if self.rotAngle == 0:
            self.accel = 1
            #
        elif self.rotAngle > 0:
            self.ang_v = radians(2)
        elif self.rotAngle < 0:
            self.ang_v = radians(-2)

        logging.debug("Robot drives forwards")
        self.cooldown(0.3)

    def driveR(self):
        "Drive the motors backwards"
        # The physical robot doesn't do this yet
        #return NotImplemented
        self.accel = -1
        logging.debug("Robot drives backwards")
        self.cooldown(0.3)

    def stop(self):
        "Stop movement motors"
        self.v[0]=0; self.v[1]=0
        self.accel = 0
        logging.debug("Robot stops driving")
        self.cooldown(0.2)

    def spinLeftShort(self):
        logging.debug("Robot does a left spin burst")
        self.cooldown(0.7)
    def spinRightShort(self):
        logging.debug("Robot does a right spin burst")
        self.cooldown(0.7)
    def tick(self):
        pass

    def setRobotDirection(self, angle):
        """
        Sends commands to the robot to steer its wheels to the
        direction to permit linear travel in degrees from 0 - 360 Deg.

        The directions are measured clockwise from the top of the
        robot when facing forward. (I.E 90 Deg = Right, 180 Deg =
        Back, 270 Deg = Left)
        """
        logging.debug( "Robot sets wheel direction to %.2f deg",
                       degrees(angle) )
        if angle == 0:
            return
        self.cooldown(0.7)

    def setRotationDir(self, angle):
        self.rotAngle = angle
    def startSpinLeft(self):
        "Turn counter-clockwise"
        self.setRotationDir(pi/2)
        #self.ang_v = radians(2)
        logging.debug("Robot spins left")
        self.cooldown(0.7)
    def startSpinRight(self):
        "Turn clockwise"
        self.setRotationDir(-pi/2)
        #self.ang_v = radians(-2)
        logging.debug("Robot spins right")
        self.cooldown(0.7)
    def stopSpin(self):
        # self.movement_dir_speed = 0
        # self.ang_v = 0
        # self.ang_accel = 0
        logging.debug("Robot stops spinning")
        self.cooldown(0.3)

    def kick(self):
        logging.info("Robot uses kick!  It's super effective!")
        self.cooldown(1.5)


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

        self.maxSpeed = 6
        self.v = np.array([0.0, 0.0])
        self.accel = 0

        self.ang_v = 0 # The speed at which the robot visibly turns
        self.ang_accel = 0
        self.rotAngle = 0

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

    def kick(self):
        logging.info("Robot uses kick!  It's super effective!")
        self.cooldown('kick', 1.5)


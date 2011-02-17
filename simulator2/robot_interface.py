from communication.interface import *
import numpy as np
from math import *
import logging, time

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

    max_speed = 100
    max_ang_v = 10
    accel = 10
    ang_accel = 0.6
    friction = 0.8

    def __init__(self, *args):
        RobotInterface.__init__(self, *args)

        self.drive_left_accel  = 0
        self.drive_right_accel = 0
        self.steer_left_accel  = 0
        self.steer_right_accel = 0

        self.steer_left_until  = 0
        self.steer_right_until = 0
        self.cooldowns = {}

        self.log = logging.getLogger("simulator2.robot.%s" % self.colour)

    def tick(self, *args):
        #RobotInterface.tick(self, *args)
        self.update_velocity( self.wheel_left.body.velocity,
                              self.drive_left_accel, self.wheel_left.body.angle )
        self.update_velocity( self.wheel_right.body.velocity,
                              self.drive_right_accel, self.wheel_right.body.angle )

        # print self.steer_left_accel
        # print self.wheel_right.body.velocity, self.wheel_left.body.velocity
        # print self.wheel_left.body.angle
        # print self.wheel_right.body.angle

        self.wheel_left.body.velocity *= self.friction
        self.wheel_right.body.velocity *= self.friction

        v = self.wheel_left.body.angular_velocity
        if v == 0:
            v = self.steer_left_accel
        else:
            v *= min(v + self.steer_left_accel, self.max_ang_v)/abs(v)
        v *= self.friction

        v = self.wheel_right.body.angular_velocity
        if v == 0:
            v = self.steer_right_accel
        else:
            v *= min(v + self.steer_right_accel, self.max_ang_v)/abs(v)
        v *= self.friction

    def cooldown(self, name, secs):
        """Wait the specified amount of seconds until the next command
        is possible.
        """
        return True

        if name not in self.cooldowns:
            self.cooldowns[name] = 0

        if self.cooldowns[name] <= time.time():
            self.cooldowns[name] = time.time() + secs
            return True
        else:
            return False

    def reset(self):
        """Puts the robot's wheels in their default setting of 0 Deg

        The direction is relative to the robot's orientation.
        """
        if self.cooldown('reset', 0.5):
            pass

    def update_velocity(self, v, accel, angle):
        mag = sqrt(sum( v**2 ))
        if mag == 0:
            v[0] = cos(angle) * accel
            v[1] = sin(angle) * accel
        else:
            new_mag = min(mag + abs(accel), self.max_speed)
            v *= new_mag / mag

    def drive_left(self, speed):
        self.log.debug("drive left %d", speed)
        if self.cooldown('drive_left', 0.1):
            self.drive_left_accel = self.accel * speed

    def drive_right(self, speed):
        self.log.debug("drive right %d", speed)
        if self.cooldown('drive_right', 0.1):
            self.drive_right_accel = self.accel * speed

    epsilon = radians(10)
    def steer_left(self, angle):
        angle = radians(angle)
        if self.steer_left_until <= self.wheel_left.body.angle:
            self.wheel_left.body.angular_velocity = 0
            return
        if angle < self.epsilon:
            return

        self.steer_left_accel = copysign(self.ang_accel, angle)
        self.steer_left_until = self.wheel_left.body.angle - angle

    def steer_right(self, angle):
        if self.steer_right_until < self.wheel_right.body.angle:
            self.wheel_right.body.angular_velocity = 0
            return
        if angle < self.epsilon:
            return

        self.steer_right_accel = copysign(self.ang_accel, angle)
        self.steer_right_until = self.wheel_right.body.angle - angle

    def kick(self):
        if self.cooldown('kick', 1.5):
            self.log.info("Robot uses kick!  It's super effective!")


from communication.interface import *
import pymunk
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

    accel = 10
    ang_accel = 3
    friction = 0.8
    epsilon = radians(3)

    def __init__(self, *args):
        RobotInterface.__init__(self, *args)

        self.drive_left_accel  = 0
        self.drive_right_accel = 0
        self.steer_left_accel  = 0
        self.steer_right_accel = 0

        self.steer_left_target  = 0
        self.steer_right_target = 0
        self.delta_left_prev    = 0
        self.delta_right_prev   = 0

        self.cooldowns = {}

        self.log = logging.getLogger("simulator2.robot.%s" % self.colour)
        self.log.setLevel(logging.DEBUG)

    def tick(self, *args):
        RobotInterface.tick(self, *args)

        self.update_velocity( self.wheel_left.body.velocity,
                              self.drive_left_accel,
                              self.wheel_left.body.angle )
        self.update_velocity( self.wheel_right.body.velocity,
                              self.drive_right_accel,
                              self.wheel_right.body.angle )

        # print self.steer_left_accel
        # print self.wheel_right.body.velocity, self.wheel_left.body.velocity
        # print degrees(self.wheel_left.body.angle) % 360
        # print degrees(self.wheel_right.body.angle) % 360

        self.wheel_left.body.velocity *= self.friction
        self.wheel_right.body.velocity *= self.friction

        delta_left = abs(
            self.get_relative_angle(self.steer_left_target,
                                    self.wheel_left.body.angle))

        diff = delta_left - self.delta_left_prev
        #if delta_left <= self.epsilon or abs(diff) > pi/2:
        if abs(diff) > pi/2:
            print delta_left, diff
            self.steer_left_accel = 0
        self.delta_left_prev = delta_left

        delta_right = abs(
            self.get_relative_angle(self.steer_right_target,
                                    self.wheel_right.body.angle))

        diff = delta_right - self.delta_right_prev
        #if delta_right <= self.epsilon or abs(diff) > pi/2:
        if abs(diff) > pi/2:
            print delta_right, diff
            self.steer_right_accel = 0
        self.delta_right_prev = delta_right

        self.wheel_left.body.angular_velocity \
            += self.steer_left_accel
        self.wheel_right.body.angular_velocity \
            += self.steer_right_accel

        v = self.wheel_left.body.angular_velocity
        v *= self.friction

        v = self.wheel_right.body.angular_velocity
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
        self._kick = True
        if self.cooldown('reset', 0.5):
            pass

    def update_velocity(self, v, accel, angle):
        v[0] += cos(angle) * accel
        v[1] += sin(angle) * accel
        v *= self.friction

    def drive_left(self, speed):
        self._drive1 = speed
        self.log.debug("drive left %d", speed)
        if self.cooldown('drive_left', 0.1):
            self.drive_left_accel = self.accel * speed

    def drive_right(self, speed):
        self._drive2 = speed
        self.log.debug("drive right %d", speed)
        if self.cooldown('drive_right', 0.1):
            self.drive_right_accel = self.accel * speed

    def get_relative_angle(self, _angle, wheel_angle):
        angle = (_angle + self.robot.body.angle - wheel_angle) % (2*pi)
        if angle <= pi:
            return angle
        else:
            return pi - angle

    def steer_left(self, angle):
        self._steer_left = angle
        self.log.debug("steer left: %d", -180+int(degrees(angle)%360))
        delta = self.get_relative_angle(angle, self.wheel_left.body.angle)

        self.steer_left_accel = copysign(self.ang_accel, delta)
        self.steer_left_target = angle
        self.delta_left_prev = abs(delta)

    def steer_right(self, angle):
        self._steer_right = angle
        self.log.debug("steer right: %d", -180+int(degrees(angle)%360))
        delta = self.get_relative_angle(angle, self.wheel_right.body.angle)

        self.steer_right_accel = copysign(self.ang_accel, delta)
        self.steer_right_target = angle
        self.delta_right_prev = abs(delta)

    def kick(self):
        self._kick = True
        if self.kickzone.point_query(self.sim.ball.body.position):
            # TODO: somehow the ball is not registered as being within
            # the kickzone. Fix that, somehow.
            self.log.info("Robot uses kick... it's super effective!")
            self.sim.ball.body.apply_impulse( (100*cos(self.robot.body.angle),
                                               100*sin(self.robot.body.angle)), (0,0))
        else:
            self.log.info("Robot uses kick... no effect")

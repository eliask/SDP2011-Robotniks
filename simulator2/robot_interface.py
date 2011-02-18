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

    max_speed = 100
    max_ang_v = 10
    accel = 10
    ang_accel = 3
    friction = 0.8
    epsilon = radians(10)

    def __init__(self, *args):
        RobotInterface.__init__(self, *args)

        self.drive_left_accel  = 0
        self.drive_right_accel = 0
        self.steer_left_accel  = 0
        self.steer_right_accel = 0

        self.steer_left_until  = 0
        self.steer_right_until = 0
        self.prev_left_angle   = 0
        self.prev_right_angle  = 0
        self.cooldowns = {}

        self.log = logging.getLogger("simulator2.robot.%s" % self.colour)
        self.log.setLevel(logging.INFO)

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
        # print self.wheel_left.body.angle
        # print self.wheel_right.body.angle

        self.wheel_left.body.velocity *= self.friction
        self.wheel_right.body.velocity *= self.friction

        #print self.steer_left_until, self.wheel_left.body.angle

        delta_left = abs(self.wheel_left.body.angle
                         - self.prev_left_angle)
        self.steer_left_until -= delta_left
        self.prev_left_angle = self.wheel_left.body.angle

        delta_right = abs(self.wheel_right.body.angle
                          - self.prev_right_angle)
        self.steer_right_until -= delta_right
        self.prev_right_angle = self.wheel_right.body.angle

        if self.steer_left_until <= self.epsilon:
            self.steer_left_accel = 0
        if self.steer_right_until <= self.epsilon:
            self.steer_right_accel = 0

        self.wheel_left.body.angular_velocity \
            += self.steer_left_accel
        self.wheel_right.body.angular_velocity \
            += self.steer_right_accel

        v = self.wheel_left.body.angular_velocity
        if v > self.max_ang_v:
            v *= self.max_ang_v / abs(v)
        v *= self.friction

        v = self.wheel_right.body.angular_velocity
        if v > self.max_ang_v:
            v *= self.max_ang_v / abs(v)
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
        v_mag = sqrt(sum( v**2 ))
        if v_mag > self.max_speed:
            v *= self.max_speed / v_mag
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

    def steer_left(self, angle):
        self._turn1 = angle
        angle = radians(angle)
        self.steer_left_accel = copysign(self.ang_accel, angle)
        self.steer_left_until = abs(angle)

    def steer_right(self, angle):
        self._turn2 = angle
        angle = radians(angle)
        self.steer_right_accel = copysign(self.ang_accel, angle)
        self.steer_right_until = abs(angle)

    def kick(self):
        self._kick = True
        self.log.info("Robot uses kick!  It's super effective!")
        return

        if self.cooldown('kick', 1.5):
            if self.kickzone.point_query(ball.body.position):
                ball.body.apply_impulse((100*cos(robot.body.angle),
                                         100*sin(robot.body.angle)), (0,0))


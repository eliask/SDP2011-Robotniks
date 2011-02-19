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
        self.log.setLevel(logging.INFO)

    def tick(self, *args):
        #RobotInterface.tick(self, *args)

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
            self.steer_left_accel = 0
        self.delta_left_prev = delta_left

        delta_right = abs(
            self.get_relative_angle(self.steer_right_target,
                                    self.wheel_right.body.angle))

        diff = delta_right - self.delta_right_prev
        #if delta_right <= self.epsilon or abs(diff) > pi/2:
        if abs(diff) > pi/2:
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

    def reset(self):
        """Puts the robot's wheels in their default setting of 0 Deg

        The direction is relative to the robot's orientation.
        """
        self._reset = True

    def update_velocity(self, v, accel, angle):
        v[0] += cos(angle) * accel
        v[1] += sin(angle) * accel
        v *= self.friction

    def drive_left(self, speed):
        self._drive_left = speed
        self.log.debug("drive left: %d", speed)
        self.drive_left_accel = self.accel * speed

    def drive_right(self, speed):
        self._drive_right = speed
        self.log.debug("drive right: %d", speed)
        self.drive_right_accel = self.accel * speed

    def get_relative_angle(self, _angle, wheel_angle):
        angle = (_angle + self.robot.body.angle - wheel_angle) % (2*pi)
        if angle <= pi:
            return angle
        else:
            return pi - angle

    def steer_left(self, angle):
        if self.drive_left_accel > 0:
            return

        self._steer_left = degrees(angle) % 360
        self.log.debug("steer left: %d", -180+int(degrees(angle)%360))
        delta = self.get_relative_angle(angle, self.wheel_left.body.angle)

        self.steer_left_accel = copysign(self.ang_accel, delta)
        self.steer_left_target = angle
        self.delta_left_prev = abs(delta)

    def steer_right(self, angle):
        if self.drive_right_accel > 0:
            return

        self._steer_right = degrees(angle) % 360
        self.log.debug("steer right: %d", -180+int(degrees(angle)%360))
        delta = self.get_relative_angle(angle, self.wheel_right.body.angle)

        self.steer_right_accel = copysign(self.ang_accel, delta)
        self.steer_right_target = angle
        self.delta_right_prev = abs(delta)

    def steer_left_incr(self, angle):
        "A helper function for the UI _only_"
        delta = radians(angle) + self.steer_left_target
        self.steer_left(delta)
    def steer_right_incr(self, angle):
        "A helper function for the UI _only_"
        delta = radians(angle) + self.steer_right_target
        self.steer_right(delta)

    def macro_steer(self, fn, angle):
        if abs(angle) == 1:
            return
            goal = pymunk.Vec2d(self.sim.goal_x, self.sim.goal_y)
            delta = goal - self.robot.body.position
            _angle = atan2(delta[1], delta[0]) - self.robot.body.angle
            print "ANGLE:", _angle, atan2(*delta)
            print "ASD:", self.get_relative_angle( atan2(delta[1], delta[0]), 0)
            fn(_angle) # * angle)
        fn( radians(angle) )

    def macro_steer_left(self, angle):
        self.macro_steer(self.steer_left, angle)
    def macro_steer_right(self, angle):
        self.macro_steer(self.steer_right, angle)

    def stop_steer(self):
        """A helper function for reinforcement learning purposes.

        The reinfrocement learning software can randomly re-initialise
        the robot's position and pose. Since the wheels can be in any
        orientation as a result, we want to stop the otherwise
        automatic steering movement and "start from scratch".
        """
        self.steer_left_accel = 0
        self.steer_right_accel = 0

    def kick(self):
        self._kick = True
        if self.kickzone.point_query(self.sim.ball.body.position):
            # TODO: somehow the ball is not registered as being within
            # the kickzone. Fix that, somehow.
            self.log.info("Robot uses kick... it's super effective!")
            self.sim.ball.body.apply_impulse( (50*cos(self.robot.body.angle),
                                               50*sin(self.robot.body.angle)), (0,0))
        else:
            self.log.info("Robot uses kick... no effect")

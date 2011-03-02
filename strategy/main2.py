from common.utils import *
from common.world import *
from communication.interface import *
from math import *
from strategy import *
import apf, functions
import logging
import pygame

class Main2(Strategy):
    turn_until = 0

    def __init__(self, *args, **kwargs):
        if not 'name' in kwargs:
            kwargs['name'] = 'main2'
        Strategy.__init__(self, *args, **kwargs)
        self.reset()

        # Variables for tracking the robot's internal state
        self.left_angle = 0
        self.right_angle = 0
        self.until_turned = 0

        self.lock_until = 0
        self.post_lock = lambda:None

        self.positions = []

    def watch_stuck(self):
        self.positions.insert(0, list(self.me.pos))
        if len(self.positions) < 25: return
        self.positions.pop()

        std = np.std( np.array(self.positions), 0 )
        if (std < 2).all():
            self.steer_both(0)
            self.drive_both(-3)
            self.kick()
            self.positions = []
            self.lock_until = self.getTimeUntil(0.2)
            self.log.warn("Detected robot being stuck, locking to backwards movement")
            return True
        else:
            return False

    def run(self):
        if self.lock_until > time.time():
            return
        else:
            if self.post_lock(): return
            self.post_lock = lambda:None

        try:
            self.me = self.getSelf() # Find out where I am
            self.log.debug("My position: %s", pos2string(self.me.pos))
        except Exception, e:
            self.log.warn("couldn't find self: %s", e)
            return

        if self.watch_stuck(): return

        ballPos = np.array( self.world.getBall().pos )
        goal = self.getMyGoalPoints()
        other_goal = self.getOpponentGoalPoints()
        opp = self.getOpponent()
        # print functions.computeGoalKicks(
        #     goal, other_goal, ballPos, opp,
        #     self.world.getResolution() )

        #print self.me.pos, ballPos
        if self.me.pos[0] == 0 or ballPos[0] == 0:
            self.stop()
            print "POS 0"
            return

        def pf(pos):
            """Calculate the potential field gradient at point

            The gradient of the potential field tells us which
            direction we should be going towards.
            """
            v = apf.all_apf( pos, self.world.getResolution(), ballPos,
                             self.getOpponentGoalPos(), World.BallRadius )

            if self.sim:
                # If in the simulator, visualise "intended movement direction"
                pos = self.me.pos
                v2 = np.array(v) * 5
                delta = map(lambda x:int(round(x)), (pos[0]+v2[0], pos[1]+v2[1]))
                #print pos, delta
                pygame.draw.line(self.sim.screen, (123,0,222,130), pos, delta, 4)
                #pygame.draw.circle(self.sim.screen, (255,50,255,130), delta, 6)

            return np.array(v)

        # Move towards the pseudo-target (which we get by adding the
        # gradient to our current position)
	# if self.orientToKick():
        #     self.moveTo(self.me.pos + 100*pf(self.me.pos))

        # # Kick the ball if we are in front of it
	# if self.canKick(ballPos):
        #     self.kick()

        self.moveTo(self.me.pos + 10*pf(self.me.pos))

        # if self.reachesGoal():
        #     print "REACH"
        #     self.dash()

        #self.sendMessage()
        return
        self.scoreGoal(ballPos)

    def reachesGoal(self):
        _,Y = self.world.getResolution()
        X,_ = self.getOpponentGoalPos()
        y1 = 1/3.0 * Y
        y2 = 2/3.0 * Y
        points = [self.me.pos, (X,y1), (X,y2)]

        ball = self.world.getBall().pos
        if dist(self.me.pos, np.array(ball)) > 100 or X-ball[0] > 100:
            return False
        if ball[0] >= self.me.pos:
            return False

        return pointInConvexPolygon(points, ball)


    def canKick(self, target_pos):
        """Are we right in front of the ball, being able to kick it?

        Note: Somewhat inaccurate atm. Adjusting the constants might work.
        """
	if dist(self.me.pos, target_pos) < 20:
            angle_diff = self.me.orientation % (2*pi)
            - pi - abs( atan2(self.me.pos[1] - target_pos[1],
                              (self.me.pos[0] - target_pos[0])) )

            return angle_diff < radians(13)

    def scoreGoal(self, ballPos):
        if self.moveTo( ballPos ): # are we there yet?
            self.kick()

    def moveTo(self, dest):
        """Move to the destination

        moveTo requires than the wheels are both pointing towards the
        wanted destination. If they are, turning is stopped and
        driving commands are issued.
        """
        if not self.turnTo(dest):
            #self.drive_both(0)
            return False

        self.log.debug("moveTo(%s)", pos2string(dest))
        #print dest, self.me.pos, type(dest), type(self.me.pos)
        _dist = dist(dest, self.me.pos)
        #print _dist
        #print dest
        self.log.debug("Distance to target: %.3f" % _dist)
        epsilon = 100

        self.drive_both(3)
        # TODO: implement the canKick predicate instead
        if _dist < epsilon:
            if self.orientToKick():
                self.drive_both(3)
            return True
        else:
            self.drive_both(3)
            return False

    def turnTo(self, dest):
        """Turn to make the _wheels_ face the destination.

        This makes the robot turn its wheels until the estimated
        orientation of both wheels is about the same as the angle to
        the destination. While the wheels are turning, the robot will
        not drive.
        """
        angle = atan2(dest[1], dest[0])
        self.log.debug("turnTo(%.1f)", degrees(angle))

        dx,dy = dest - self.me.pos
        angle = atan2(dy,dx)
        orient = self.me.orientation
        delta = angle - orient
        self.steer_both(delta)
        self.log.debug( "steer_both(%.1f)", degrees(delta) )

        d_left = delta - self.left_angle
        d_right = delta - self.right_angle
        #print delta

        if self.until_turned < time.time():
            self.until_turned = self.getTimeUntil(0.6)
            self.left_angle = self.right_angle = delta
            #print self.until_turned
            d_left = d_right = 0

        if angleDiffWithin(abs(d_left), radians(20)) and \
                angleDiffWithin(abs(d_right), radians(20)):
            #print d_left, d_right
            return True
        else:
            self.drive_both(0)
            return False

    def dash(self):
        if True or self.orientToKick():
            self.lock_until = self.getTimeUntil(1.8)
            self.post_lock = self.kick
            self.drive_both(3)

    def orientToKick(self):
        """Orient the robot's body to face the ball.

        The robot will first orient the wheels to a position that allows
        """
        self.log.debug("orientToKick()")

        ball = self.getBall().pos
        goal = self.getOpponentGoalPos()
        dx,dy = goal[0]-ball[0], goal[1]-ball[1]
        angle = atan2(dy,dx)
        delta = abs(angle - self.me.orientation) % (2*pi)
        self.log.debug( "Difference between orientation and kicking angle: %.1f",
                        degrees(delta) )

        if angleDiffWithin(delta, radians(40)):
            self.turn_until = 0
            self.drive_both(0)
            return True
        else:
            if self.turn_until == 0:
                self.turn_until = self.getTimeUntil(0.7)
                self.drive_both(0)

            if delta <= pi:
                self.steer_left(radians(135))
                self.steer_right(radians(-45))
            else:
                self.steer_left(radians(-45))
                self.steer_right(radians(135))

            if self.turn_until < time.time():
                self.drive_both(3)
            return False

    def orient(angle):
        """Change the robot's orientation to specified angle.

        The robot will be turned in a way that minimises the turning
        time, taking into account wheel turning direction and driving
        direction.
        """
        pass

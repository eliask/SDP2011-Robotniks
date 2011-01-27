from pygame.locals import *
import pygame
from math import *
from random import *
from .common.utils import *
from world import World
from entity import Entity
import logging

class Robot(Entity):
	
    size = (59, 38)
    maxSpeed = 6

    def __init__(self, sim, pos, image, orientation):
        self.orientation = orientation
        self.accel = 0

        self.ang_v = 0
        self.ang_accel = 0

        self.movementDir = 0
        self.turning_speed = 0 # The speed at which the wheels turn

        Entity.__init__(self, sim, pos, image)
        self.rotate()

    def reset(self):
        """Puts the robot's wheels in their default setting of 0 Deg

        The direction is relative to the robot's orientation.
        """
        # TODO: make this take time, like acceleration
	self.movementDir = self.orientation

    def drive(self):
        "Drive the motors forwards"
        self.accel = 1
        logging.debug("Robot drives forwards")
    def driveR(self):
        "Drive the motors backwards"
        # The physical robot doesn't do this yet
        #return NotImplemented
        self.accel = -1
        logging.debug("Robot drives backwards")
    def stop(self):
        "Stop movement motors"
        self.v[0]=0; self.v[1]=0
        self.accel = 0
        logging.debug("Robot stops driving")
    def spinLeftShort(self):
        logging.debug("Robot does a left spin burst")
    def spinRightShort(self):
        logging.debug("Robot does a right spin burst")
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
        return NotImplemented

    def startSpinLeft(self):
        "Turn counter-clockwise"
        self.ang_v = radians(2)
        logging.debug("Robot spins left")
    def startSpinRight(self):
        "Turn clockwise"
        self.ang_v = radians(-2)
        logging.debug("Robot spins right")
    def stopSpin(self):
        self.ang_v = 0
        self.ang_accel = 0
        logging.debug("Robot stops spinning")
    def updateDirection(self):
        self.movementDir += self.turning_speed

    def kick(self):
        logging.info("Robot uses kick!  It's super effective!")

    def rotate(self):
        rot_img = pygame.transform.rotate(self.base_image,
                                          degrees(self.orientation))
        img_rect = rot_img.get_rect()
        img_rect.center = self.pos
        self.rect = img_rect
        self.image = rot_img

    def savePos(self):
        "Save current position, in case we want to revert it"
        self.prevRect = self.rect
        self.prevPos  = self.pos

    def undoMove(self):
        self.rect = self.prevRect
        self.pos  = self.prevPos

    def move(self):
        Entity.move(self)
        self.orientation += self.ang_v
        self.rotate()

    def update(self):
        self.move()

        # The rectangle's center should always be at or very near the
        # position of the robot since we want the rotation and the
        # subsequent collision detection to be accurate. If the
        # rotation and the collision detection can be made to work
        # some other way, this assertion can be removed.
        #print self.rect.center, self.pos
        assert self.rect.center == (floor(self.pos[0]), floor(self.pos[1]))

        self.savePos()
        self.updateVelocity()
        self.updateDirection()
        self.collideRobot()

        pygame.draw.circle(self.sim.overlay, (0,0,140,255),
                           map(int, self.pos), 20)

        #self.randomMove()
        if not World.Pitch.contains(self.rect):
            # A hack--if we would leave the area somehow, we will
            # completely reverse the would be move.
            self.undoMove()

    def updateVelocity(self):
        mag = sqrt(sum(self.v**2))
        if mag == 0:
            self.v[0] = cos(self.movementDir) * self.accel
            self.v[1] = sin(self.movementDir) * self.accel
        else:
            newMag = min(mag + abs(self.accel), self.maxSpeed)
            self.v *= newMag / mag

    def randomMove(self):
        self.v += randint(-4,4)
        self.v[0] = clamp(-8, self.v[0], 8)
        self.v[1] = clamp(-8, self.v[1], 8)

        self.rect = self.rect.move(self.v)
        self.ang_v += radians(randint(-4,4))
        self.ang_v = radians(clamp(-8, self.ang_v, 8))
        # TODO: also rotate the 'rect' somehow
        self.orientation += self.ang_v
        self.rotate()

    def collideRobot(self):
        other = [ robot for robot in self.sim.robots
                  if robot.side != self.side ][0]

        selfCorners  = self.boundingBoxCorners(self)
        otherCorners = self.boundingBoxCorners(other)

        selfLines  = self.getLines(selfCorners)
        otherLines = self.getLines(otherCorners)
        pygame.draw.lines(self.sim.overlay, (255,0,0,255), True,
                            selfCorners, 5)
        # pygame.draw.aalines(self.sim.screen, (240,248,255,255), True,
        #                     [c[0] for c in selfLines], 5)

        collisions = []
        for i in selfLines:
            for j in otherLines:
                point = self.intersectLines(i, j)
                if point and self.collideBox(selfLines, point, otherLines):
                    # We only test one of the robots for this as the
                    # intersections are the same with either
                    collisions.append(point)

        if collisions:
            self.repulseRobot(collisions)

    def repulseRobot(self, points):
        """Apply force to the robot to move it away from the collision
        point(s)

        For now, we simply undo the last movement. Ideally we would
        move to the normal of the line that contains the two
        intersecting lines of the robot's rectangle shape.
        """
	print random(), "Collision"
        self.undoMove()

    def collideBox(self, lines, point, otherLines):
        "Test whether a given line intersection point collides with a box"
        for p0, slope, p1 in lines:
		for r0, slope2, r1 in otherLines:
			if inRange(p0[0], point[0], p1[0]) and inRange(p0[1], point[1], p1[1]) and inRange(r0[0], point[0], r1[0]) and inRange(r0[1], point[1], r1[1]):
				return True

        return False

    def intersectLines(self, line1, line2):

        (x10, y10), slope1, (x11, y11) = line1
        (x20, y20), slope2, (x21, y21) = line2

        if slope1 == slope2:
            # Even if the lines are the same, we can't pick a unique
            # point. For simplicity, we don't consider that to be a
            # collision.
            return None
	
        #if slope1 is None:
        #    return (x10, x20 + slope2*x10)
        #if slope2 is None:
        #    return (x20, x10 + slope1*x20)
	m1 = y10 - slope1 * x10
	m2 = y20 - slope2 * x20
        x = (m2 - m1) / (slope1 - slope2)
        y = m1 + slope1 * x
        return (x, y)

    def getLines(self, corners):
        # Get lines from corner points
        lines = []
	i = -1
	for c in corners:
	    c2 = c
	    c1 = corners[i]
	    i += 1
            dy, dx = c1[1] - c2[1], c1[0] - c2[0]
            if dx == 0:
                slope = 0.0
            else:
                slope = dy / dx
            lines.append( (c1, slope, c2) )
        return lines

    def boundingBoxCorners(self, ent):
        W, H   = self.size
	pX, pY = ent.pos
	pX -= W / 2 
	pY -= H / 2 
	corners = [ (pX, pY), (pX+W, pY), (pX+W, pY+H), (pX, pY+H) ]
	return rotatePoints(corners, ent.pos, -ent.orientation)
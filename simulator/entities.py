from pygame.locals import *
import pygame
import numpy as np
from random import *
from math import *
from world import World
from .common.utils import *

RobotDim = (54, 36)
BallDim  = (12, 12)
Friction = 0.03

class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, image, sim):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.image = image
        self.sim = sim
        self.base_image = image
        self.v = [0.0, 0.0]

class Ball(Entity):
    def __init__(self, pos, image, sim):
        Entity.__init__(self, pos, image, sim)

    def update(self):
        self.reflectWall()
        self.collideRobots()
        self.applyFriction()
        self.move()

    def move(self):
        self.pos = ( self.pos[0] + self.v[0], self.pos[1] + self.v[1] )
        self.rect.center = self.pos

    def reflectWall(self):
        if self.rect.top < World.Pitch.top \
        or self.rect.bottom > World.Pitch.bottom:
            self.v[1] = -self.v[1]

        if self.rect.left < World.Pitch.left and \
                ( self.rect.top    > LeftGoalArea.top or
                  self.rect.bottom > LeftGoalArea.bottom ):
                self.v[0] = -self.v[0]

        elif self.rect.right > World.Pitch.right and \
                ( self.rect.top    > RightGoalArea.top or
                  self.rect.bottom > RightGoalArea.bottom ):
                self.v[0] = -self.v[0]

    def collideRobots(self):
        for robot in self.sim.robots:
            self.collideRobot(robot)

    def collideRobot(self, robot):
        return NotImplemented

    def applyFriction(self):
        q = sqrt(self.v[0]**2 + self.v[1]**2)
        if q <= Friction:
            self.v = [0.0, 0.0]
        else:
            self.v[0] = self.v[0] - Friction * self.v[0] / q
            self.v[1] = self.v[1] - Friction * self.v[1] / q

class Robot(Entity):
    def __init__(self, pos, image, angle, sim):
        Entity.__init__(self, pos, image, sim)
        self.angle = angle
        self.w = 0
        self.turn(angle)

    def turn(self, angle):
        self.angle = angle
        self.image = pygame.transform.rotate(self.base_image, angle)

    def savePos(self):
        "Save current position, in case we want to revert it"
        self.prevRect = self.rect

    def undoMove(self):
        self.rect = self.prevRect

    def update(self):
        self.savePos()
        self.collideRobot()

        self.v[0] += randint(-4,4)
        self.v[1] += randint(-4,4)
        self.v[0] = clamp(-8, self.v[0], 8)
        self.v[1] = clamp(-8, self.v[1], 8)

        self.rect = self.rect.move(self.v)
        if not World.Pitch.contains(self.rect):
            # A hack--if we would leave the area somehow, we will
            # completely reverse the would be move.
            self.undoMove()

        self.w += randint(-4,4)
        self.w = clamp(-8, self.w, 8)
        # TODO: also rotate the 'rect' somehow
        self.turn(self.angle + self.w)

    def collideRobot(self):
        other = [ robot for robot in self.sim.robots
                  if robot.side != self.side ][0]

        selfCorners  = self.boundingBoxCorners(self)
        otherCorners = self.boundingBoxCorners(other)

        selfLines  = self.getLines(selfCorners)
        otherLines = self.getLines(otherCorners)

        collisions = []
        for i in selfLines:
            for j in otherLines:
                point = self.intersectLines(i, j)
                if point and self.collideBox(selfLines, point):
                    # We only test one of the robots for this as the
                    # intersections are the same with either
                    collisions.append(point)

        if collisions:
            self.repulseRobot(collisions)

    def repulseRobot(self, points):
        """Apply force to the robot to move it away from the collision point(s)

        For now, we simply undo the last movement
        """
        self.undoMove()

    def collideBox(self, lines, point):
        "Test whether a given line intersection point collides with a box"
        for p0, slope, p1 in lines:
            if slope == None:
                if inRange(p1[1], point[1], p0[1]) and approxZero(point[0] - x0):
                    return True
            else:
                Y = p0[0] + slope * point[0]
                if inRange(p0[1], Y, p1[1]) and approxZero(Y - point[1]):
                    return True

        return False

    def intersectLines(self, line1, line2):
        """Determine where lines intersect.
        :: Line -> Line -> Maybe Pos
        """
        (x10, y10), slope1, (x11, y11) = line1
        (x20, y20), slope2, (x21, y21) = line2

        if slope1 == slope2:
            # Even if the lines are the same, we can't pick a unique
            # point. For simplicity, we don't consider that to be a
            # collision.
            return None

        if slope1 is None:
            return (x10, x20 + slope2*x10)
        if slope2 is None:
            return (x20, x10 + slope1*x20)

        X = (x20 - x10) / (slope1 - slope2)
        y1 = x10 + slope1 * X
        y2 = x20 + slope2 * X
        assert approxZero(y1 - y2, epsilon=0.1), "Non-parallel lines don't intersect?!"

        return (X, y1)

    def getLines(self, corners):
        """Get lines from corner points
        :: [ (X,Y) ] -> [ (pos0, Maybe( dy/dx ), pos1) ]

        The lines form a convex hull.
        """
        lines = []
        for c1, c2 in zip( corners, corners[-1:] + corners[1:] ):
            dy, dx = c2[1] - c1[1], c2[0] - c1[0]
            if dx == 0:
                slope = None
            else:
                slope = dy / dx
            lines.append( (c1, slope, c2) )
        return lines

    def boundingBoxCorners(self, ent):
        pX, pY = ent.pos
        W, H   = RobotDim
        corners = [ (pX, pY), (pX+W, pY), (pX+W, pY+H), (pX, pY+H) ]
        return rotatePoints(corners, ent.rect.center, ent.angle)


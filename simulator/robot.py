from pygame.locals import *
import pygame
from math import *
from random import *
from .common.utils import *
from world import World
from entity import Entity

class Robot(Entity):

    maxSpeed = 6

    def __init__(self, sim, pos, image, orientation):
        Entity.__init__(self, sim, pos, image)
        self.orientation = orientation
        self.ang_v = 0
        self.ang_accel = 0
        self.accel = 0
        self.rotate(orientation)
        self.movementDir = 0

    def reset(self):
        "Puts the robot's wheels in their default setting of 0 Deg"
        pass

    def drive(self):
        "Drive the motors forwards"
        self.accel = 1
    def driveR(self):
        "Drive the motors backwards"
        # The physical robot doesn't do this yet
        #return NotImplemented
        self.accel = -1
    def stopDrive(self):
        "Stop movement motors"
        self.v[0]=0; self.v[1]=0
        self.accel = 0

    def setDirection(self, angle):
        """
        Sends commands to the robot to steer its wheels to the
        direction to permit linear travel in degrees from 0 - 360 Deg.

        The directions are measured clockwise from the top of the
        robot when facing forward. (I.E 90 Deg = Right, 180 Deg =
        Back, 270 Deg = Left)
        """
        if angle == 0:
            return
        return NotImplemented

    def turn(self):
        "Turn counter-clockwise"
        self.ang_v = 2
    def turnR(self):
        "Turn clockwise"
        self.ang_v = -2
    def stopTurn(self):
        self.ang_v = 0
        self.ang_accel = 0
    def updateDirection(self):
        self.movementDir += self.ang_v

    def startSpin(self):
        pass
    def stopSpin(self):
        pass
    def kick(self):
        pass

    def stopAll(self):
        self.stopMove1()
        self.stopMove2()
        self.stopRot1()
        self.stopRot2()

    def move1(self):
        pass
    def move1R(self):
        pass
    def stopMove1(self):
        pass

    def move2(self):
        pass
    def move2R(self):
        pass
    def stopMove2(self):
        pass

    def stopRot1(self):
        pass
    def rot1(self):
        pass
    def rot1R(self):
        pass

    def stopRot2(self):
        pass
    def rot2(self):
        pass
    def rot2R(self):
        pass

    def rotate(self, orientation):
        self.orientation = orientation
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

    def update(self):
        self.move()

        # The rectangle's center should always be at or very near the
        # position of the robot since we want the rotation and the
        # subsequent collision detection to be accurate. If the
        # rotation and the collision detection can be made to work
        # some other way, this assertion can be removed.
        print self.rect.center, self.pos
        assert self.rect.center == (floor(self.pos[0]), floor(self.pos[1]))

        self.savePos()
        self.updateVelocity()
        self.updateDirection()
        self.collideRobot()

        pygame.draw.circle(self.sim.overlay, (0,0,140,255), self.pos, 20)

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
        self.rotate(self.orientation + self.ang_v)

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
        pygame.display.update()

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
                if inRange(p1[1], point[1], p0[1]) \
                and approxZero(point[0] - p0[0]):
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
        #y2 = x20 + slope2 * X
        # y1 ~= y2 due to noise and numerical instability/inaccuracies
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
        pX, pY = self.rect.topleft
        W, H   = self.rect.size
        corners = [ (pX, pY), (pX+W, pY), (pX+W, pY+H), (pX, pY+H) ]
        return rotatePoints(corners, ent.pos, ent.orientation)

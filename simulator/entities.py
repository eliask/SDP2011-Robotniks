from pygame.locals import *
import pygame
from random import *
from math import *
from world import World
from .common.utils import *

RobotDim = (54, 36)
BallDim  = (12, 12)
Friction = 0.03

class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.image = image
        self.base_image = image
        self.v = [0.0, 0.0]

class Ball(Entity):
    def __init__(self, pos, image, sim):
        Entity.__init__(self, pos, image)
        self.sim = sim

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
    def __init__(self, pos, image, angle):
        Entity.__init__(self, pos, image)
        self.angle = angle
        self.w = 0
        self.turn(angle)

    def turn(self, angle):
        self.angle = angle
        self.image = pygame.transform.rotate(self.base_image, angle)

    def update(self):
        self.v[0] += randint(-4,4)
        self.v[1] += randint(-4,4)
        self.v[0] = clamp(-8, self.v[0], 8)
        self.v[1] = clamp(-8, self.v[1], 8)
        self.rect.move_ip(self.v)
        if not World.Pitch.contains(self.rect):
            # A hack--if we would leave the area somehow, we will
            # completely reverse the would be move.
            self.rect.move_ip(-self.v[0], -self.v[1])

        self.w += randint(-4,4)
        self.w = clamp(-8, self.w, 8)
        # TODO: also rotate the 'rect' somehow
        self.turn(self.angle + self.w)

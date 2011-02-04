from pygame.locals import *
import pygame
from math import *
from world import World
from entity import Entity
import numpy as np

class Ball(Entity):
    def update(self):
        self.reflectWall()
        self.collideRobots()
        self.applyFriction()
        self.move()

    def reflectWall(self):
        if self.rect.top < World.Pitch.top \
        or self.rect.bottom > World.Pitch.bottom:
            self.v[1] = -self.v[1]

        if self.rect.left < World.Pitch.left and \
                ( self.rect.top    > World.LeftGoalArea.top or
                  self.rect.bottom > World.LeftGoalArea.bottom ):
                self.v[0] = -self.v[0]

        elif self.rect.right > World.Pitch.right and \
                ( self.rect.top    > World.RightGoalArea.top or
                  self.rect.bottom > World.RightGoalArea.bottom ):
                self.v[0] = -self.v[0]

    def collideRobots(self):
        for robot in self.sim.robots:
            self.collideRobot(robot)

    def collideRobot(self, robot):
        return NotImplemented

    def applyFriction(self):
        q = sqrt(sum(self.v**2))
        if q <= World.Friction:
            self.v = np.array((0.0, 0.0))
        else:
            self.v -= World.Friction * self.v / q

from pygame.locals import *
import pygame
from math import *
from world import World
from entity import Entity

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
        if q <= World.Friction:
            self.v = [0.0, 0.0]
        else:
            self.v[0] = self.v[0] - World.Friction * self.v[0] / q
            self.v[1] = self.v[1] - World.Friction * self.v[1] / q

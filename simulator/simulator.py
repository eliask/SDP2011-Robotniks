#! /usr/bin/env python
# -*- coding: utf-8 -*-

from math import *
from random import *
from pygame.locals import *
import pygame
from utils import *

image_names = {
    'bg'     : '../vision/background.png',
    'blue'   : 'blue_robot.png',
    'yellow' : 'yellow_robot.png',
    'ball'   : 'ball.png',
    }

Resolution = (768, 576)

Pitch = Rect(37, 119, 769-37, 465-119)
LeftGoalArea= Rect(15, 207, 36-15, 377-207)
RightGoalArea= Rect(733, 207, 36-15, 377-207)

RobotDim = (54, 36)
BallDim  = (12, 12)

LeftStartPos  = ( LeftGoalArea.left + 130,
                  LeftGoalArea.top +  LeftGoalArea.height/2 )
RightStartPos = ( RightGoalArea.right - 130,
                  RightGoalArea.top + RightGoalArea.height/2 )

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
        if self.rect.top < Pitch.top or self.rect.bottom > Pitch.bottom:
            self.v[1] = -self.v[1]

        if self.rect.left < Pitch.left and \
                ( self.rect.top    > LeftGoalArea.top or
                  self.rect.bottom > LeftGoalArea.bottom ):
                self.v[0] = -self.v[0]

        elif self.rect.right > Pitch.right and \
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
        dx = randint(-4,4)
        dy = randint(-4,4)
        self.rect.move_ip((dx, dy))
        if not Pitch.contains(self.rect):
            # A hack--if we would leave the area somehow, we will
            # completely reverse the would be move.
            self.rect.move_ip((-dx, -dy))

        dw = randint(-4,4)
        # TODO: also rotate the 'rect' somehow
        self.turn(self.angle + dw)


class Simulator:

    objects=[]
    robots=[]
    images={}
    quit=False

    def drawEnts(self):
        self.screen.blit(self.images['bg'], (0,0))
        self.sprites.draw(self.screen)
        pygame.display.flip()

    def initDisplay(self):
        pygame.display.set_mode(Resolution)
        pygame.display.set_caption('SDP 9 Simulator')
        self.screen = pygame.display.get_surface()

    def makeObjects(self):
        colours = ['blue', 'yellow']
        if random() < 0.5:
            col = colours.pop()
        else:
            col = colours[0]
        other = colours.pop()

        self.makeBall(Pitch.center)
        self.makeRobot(LeftStartPos, col, 90)
        self.makeRobot(RightStartPos, other, 270)
        self.sprites = pygame.sprite.RenderPlain(self.objects)

    def run(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.initDisplay()
        self.loadImages()
        self.makeObjects()
        self.drawEnts()

        while True:
            # Currently this just freezes everything.
            #  Maybe we could do manual control of our simulated robot
            # to get a sense of how it should be programmed.
            #input(pygame.event.get())

            self.clock.tick(25)
            self.sprites.update()
            self.drawEnts()

    def input(self, events):
        for event in events:
            if event.type == QUIT:
                sys.exit(0)
            else:
                print event

    def moveEntity(self, ent):
        pass

    def makeRobot(self, pos, colour, angle):
        ent = Robot(pos, self.images[colour], angle)
        ent.rect = Rect( (pos[0] - RobotDim[0]/2,
                          pos[1] - RobotDim[1]/2),
                        RobotDim )
        self.robots.append(ent)
        self.addEnt(ent)

    def makeBall(self, pos):
        ent = Ball(pos, self.images['ball'], self)
        ent.rect = Rect( (pos[0] - BallDim[0]/2,
                          pos[1] - BallDim[1]/2),
                        BallDim )
        ent.v = [1, 7]

        self.addEnt(ent)

    def addEnt(self, ent):
        self.objects.append(ent)

    def loadImages(self):
        for name in image_names.keys():
            self.images[name] = pygame.image.load(image_names[name])

if __name__ == '__main__':
    sim = Simulator()
    sim.run()


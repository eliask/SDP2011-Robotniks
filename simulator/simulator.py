#! /usr/bin/env python
# -*- coding: utf-8 -*-

from math import *
from random import *
from pygame.locals import *
import pygame
#import pygame.image


image_names = {
    'bg'     : '../vision/background.png',
    'blue'   : 'blue_robot.png',
    'yellow' : 'yellow_robot.png',
    'ball'   : 'ball.png',
    }

Resolution = (768, 576)

Pitch = Rect(37, 119, 769-37, 465-119)
leftGoalArea= Rect(15, 207, 36-15, 377-207)
rightGoalArea= Rect(733, 207, 36-15, 377-207)

RobotDim = (54, 36)
BallDim  = (12, 12)

leftStartPos  = (  leftGoalArea.left + 130,  leftGoalArea.top +  leftGoalArea.height/2)
rightStartPos = (rightGoalArea.right - 130, rightGoalArea.top + rightGoalArea.height/2)

class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.image = image
        self.speed = 0
        self.momentum = 0 #terminology? Meaning the direction component of velocity

    def update(self):
        print "asd"
        dx = randint(-4,4)
        dy = randint(-4,4)
        self.rect.move_ip((dx, dy))
        if not Pitch.contains(self.rect):
            # A hack--if we would leave the area somehow, we will
            # completely reverse the would be move.
            self.rect.move_ip((-dx, -dy))

    def getOrientation(self):
        return self.angle
    def getSpeed(self):
        return NotImplemented
    def getPosition(self):
        return self.pos

class Simulator:

    tickSize=0.01
    objects=[]
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

        self.makeRobot(leftStartPos, col, 0)
        self.makeRobot(rightStartPos, other, -pi)
        self.makeBall(Pitch.center)
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

            self.clock.tick(100)
            self.sprites.update()
            print "tick"
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
        ent = Entity(pos, self.images[colour])
        ent.angle = angle
        ent.rect = Rect( (pos[0] - RobotDim[0]/2,
                          pos[1] - RobotDim[1]/2),
                        RobotDim )

        self.addEnt(ent)

    def makeBall(self, pos):
        ent = Entity(pos, self.images['ball'])
        ent.rect = Rect( (pos[0] - BallDim[0]/2,
                          pos[1] - BallDim[1]/2),
                        BallDim )

        self.addEnt(ent)

    def addEnt(self, ent):
        self.objects.append(ent)

    def loadImages(self):
        for name in image_names.keys():
            self.images[name] = pygame.image.load(image_names[name])

if __name__ == '__main__':
    sim = Simulator()
    sim.run()

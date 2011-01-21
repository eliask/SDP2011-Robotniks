#! /usr/bin/env python
# -*- coding: utf-8 -*-

from pygame.locals import *
import pygame
from math import *
from random import *
import tempfile
from world import World
from entities import *
from .common.utils import *
from .vision.vision import Vision

class Simulator:

    objects=[]
    robots=[]
    images={}
    headless=False
    vision=None
    quit=False

    def __init__(self, vision=False, headless=False):
        self.headless = headless
        if vision:
            self.vision = Vision(simulator=self)
            self.visionFile = tempfile.mktemp(suffix='.bmp')

    def drawEnts(self):
        self.screen.blit(self.images['bg'], (0,0))
        self.sprites.draw(self.screen)
        if not self.headless:
            pygame.display.flip()
        if self.vision:
            pygame.image.save(self.screen, self.visionFile)
            self.vision.processFrame()

    def initDisplay(self):
        pygame.display.set_mode(World.Resolution)
        pygame.display.set_caption('SDP 9 Simulator')
        self.screen = pygame.display.get_surface()

    def makeObjects(self):
        colours = ('blue', 'yellow')
        if random() < 0.5:
            col1, col2 = colours
        else:
            col2, col1 = colours

        self.makeBall(World.Pitch.center)
        self.makeRobot(World.LeftStartPos, col1, 90)
        self.makeRobot(World.RightStartPos, col2, 270)
        self.sprites = pygame.sprite.RenderPlain(self.objects)

    def run(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        if not self.headless:
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
        for name in World.image_names.keys():
            self.images[name] = pygame.image.load(World.image_names[name])

if __name__ == '__main__':
    sim = Simulator()
    sim.run()


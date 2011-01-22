#! /usr/bin/env python
# -*- coding: utf-8 -*-

from pygame.locals import *
import pygame
from math import *
from random import *
import tempfile
from world import World
from robot import *
from ball import *
from .common.utils import *
from .vision.vision import Vision
from input import Input

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
        self.world = World()
        self.overlay = pygame.Surface(World.Resolution)

    def drawEnts(self):
        self.screen.blit(self.images['bg'], (0,0))
        self.sprites.draw(self.screen)
        if self.vision:
            pygame.image.save(self.screen, self.visionFile)
            self.vision.processFrame()
        # Update overlay after we've passed the "raw image" to vision
        self.screen.blit(self.overlay, (0,0))
        # Make the overlay "blank" again. Should be completely
        # transparent but I don't know how to do that
        self.overlay.fill( (130,130,130,255))
        if not self.headless:
            pygame.display.flip()

    def initDisplay(self):
        if self.headless:
            self.screen = pygame.Surface(World.Resolution)
        else:
            pygame.display.set_mode(World.Resolution)
            pygame.display.set_caption('SDP 9 Simulator')
            self.screen = pygame.display.get_surface()
            self.overlay.convert_alpha()
            self.overlay.set_alpha(100)

    def makeObjects(self):
        colours = ('blue', 'yellow')
        if random() < 0.5:
            col1, col2 = colours
        else:
            col2, col1 = colours

        self.makeBall(World.Pitch.center)
        self.makeRobot(World.LeftStartPos, col1, 0)
        self.makeRobot(World.RightStartPos, col2, pi)
        self.sprites = pygame.sprite.RenderPlain(self.objects)

    def run(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.initDisplay()
        self.loadImages()
        self.makeObjects()
        self.initInput()
        self.drawEnts()

        while True:
            self.handleInput()
            self.clock.tick(25)
            self.drawEnts()
            self.sprites.update()

    def initInput(self):
        self.input = Input(self.robots[0], self.robots[1])

    def handleInput(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            else:
                print event
                self.input.robotInput(event)

    def makeRobot(self, pos, colour, angle):
        ent = Robot(self, pos, self.images[colour], angle)
        ent.side = colour
        self.world.ents[colour] = ent
        self.robots.append(ent)
        self.addEnt(ent)

    def makeBall(self, pos):
        ent = Ball(self, pos, self.images['ball'])
        ent.v = [1, 7]
        self.world.ents['ball'] = ent
        self.addEnt(ent)

    def addEnt(self, ent):
        self.objects.append(ent)

    def loadImages(self):
        for name in World.image_names.keys():
            self.images[name] = pygame.image.load(World.image_names[name])

if __name__ == '__main__':
    sim = Simulator()
    sim.run()


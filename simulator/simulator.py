#! /usr/bin/env python
# -*- coding: utf-8 -*-

from .common.utils import *
from .strategy.strategy import Strategy
from .vision.vision import Vision
from entities import *
from math import *
from pitch import *
from pygame.locals import *
from random import *
from world import *
import common.world
import pygame
import sys, tempfile
import communication.client

class Simulator(object):

    objects=[]
    robots=[]
    images={}

    # Options and arguments
    headless=False
    vision=None
    pitch=None
    ai=[]
    robot1=None
    robot2=None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)
            print k,v

    def initVision(self):
        if self.vision:
            world = self.world
            if not self.real_world:
                world = common.world.World(self.colour)
            self.vision = Vision(simulator=self, world=world)
            self.visionFile = tempfile.mktemp(suffix='.bmp')
            self.world = self.vision.world

    def drawEnts(self):
        if self.pitch:
            bg = self.pitch.get()
            self.screen.blit(bg, (0,0))

        self.sprites.draw(self.screen)

        if not self.headless:
            pygame.display.flip()

        if self.vision:
            pygame.image.save(self.screen, self.visionFile)
            self.vision.processFrame()

    def initScreen(self):
        if self.headless:
            self.screen = pygame.Surface(World.Resolution)
        else:
            pygame.display.set_mode(World.Resolution)
            pygame.display.set_caption('SDP 9 Simulator')
            self.screen = pygame.display.get_surface()

    def makeObjects(self):
        colours = ('blue', 'yellow')
        if random() < 0.5:
            col1, col2 = colours
        else:
            col2, col1 = colours

        self.makeRobot(World.LeftStartPos, col1, 90, self.robot1[0])
        self.makeRobot(World.RightStartPos, col2, 270, self.robot2[0])

        # Only make a real ball when there are two simulated robots
        if len(self.robots) == 2:
            self.makeBall(World.Pitch.center)

        self.sprites = pygame.sprite.RenderPlain(self.objects)

    def initAI(self):
        ai1, real1 = self.robot1
        ai2, real2 = self.robot2

        if ai1 and real1:
            self.ai.append( ai1(self.world, RealRobotInterface() ) )
            del self.robots[0]
        elif ai1:
            self.ai.append( ai1(self.world, self.robots[0]) )

        elif ai2 and real2:
            # TODO: reverse sides here
            self.ai.append( ai2(self.world, RealRobotInterface() ) )
            del self.robots[1]
        elif ai2:
            self.ai.append( ai2(self.world, self.robots[1]) )

    def run(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.initVision()
        self.initScreen()
        self.loadImages()
        self.makeObjects()
        self.world.assignSides()
        self.initAI()
        self.drawEnts()

        while True:
            self.clock.tick(25)
            self.input(pygame.event.get())
            self.sprites.update()
            self.drawEnts()
            map( lambda x: x.run(), self.ai )

    def input(self, events):
        for event in events:
            if event.type == QUIT:
                sys.exit(0)
            else:
                print event

    def makeRobot(self, pos, colour, angle, ai):
        ent = Robot(self, pos, self.images[colour], angle)
        ent.rect = Rect( (pos[0] - RobotDim[0]/2,
                          pos[1] - RobotDim[1]/2),
                        RobotDim )
        ent.side = colour

        self.world.ents[colour] = ent
        self.robots.append(ent)
        self.addEnt(ent)

    def makeBall(self, pos):
        ent = Ball(self, pos, self.images['ball'])
        ent.rect = Rect( (pos[0] - BallDim[0]/2,
                          pos[1] - BallDim[1]/2),
                        BallDim )
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


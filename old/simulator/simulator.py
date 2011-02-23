#! /usr/bin/env python
# -*- coding: utf-8 -*-

from common.utils import *
from communication.client import *
from strategy.strategy import Strategy
from ball import *
from input import Input
from math import *
from pitch import *
from pygame.locals import *
from random import *
from robot import *
from world import *
import common.world
import pygame
import sys, tempfile, logging

try:
    from vision.vision import Vision
except ImportError:
    pass

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
        logging.debug("Simulator started with the arguments:")
        for k, v in kwargs.items():
            self.__setattr__(k, v)
            logging.debug("\t%s = %s", k, v)

    def initVision(self):
        if self.vision:
            logging.info("Starting simulator vision bridge")
            world = self.world
            if not self.real_world:
                # Vision must always use the real World
                world = common.world.World(self.colour)
            self.vision = Vision(simulator=self, world=world)
            self.visionFile = tempfile.mktemp(suffix='.bmp')

    def drawEnts(self):
        if self.pitch:
            bg = self.pitch.get()
            self.screen.blit(bg, (0,0))
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

    def initScreen(self):
        logging.debug("Creating simulator screen")
        if self.headless:
            self.screen = pygame.Surface(World.Resolution)
        else:
            pygame.display.set_mode(World.Resolution)
            pygame.display.set_caption('SDP 9 Simulator')
            self.screen = pygame.display.get_surface()
            self.overlay = pygame.Surface(World.Resolution)
            self.overlay.convert_alpha()
            self.overlay.set_alpha(100)

    def makeObjects(self):
        logging.debug("Creating game objects")

        colours = ('blue', 'yellow')
        if random() < 0.5:
            col1, col2 = colours
        else:
            col2, col1 = colours

        logging.info("Robot 1 is %s. Robot 2 is %s", col1, col2)
        self.makeRobot(World.LeftStartPos, col1, 0, self.robot1[0])
        self.makeRobot(World.RightStartPos, col2, -pi, self.robot2[0])

        # Only make a real ball when there are two simulated robots
        if len(self.robots) == 2:
            pos = World.Pitch.center
            logging.info("Creating a ball at %s", pos2string(pos))
            self.makeBall(pos)
        else:
            logging.info("Not making a simulated ball with real robots")

        self.sprites = pygame.sprite.RenderPlain(self.objects)

    def setRobotAI(self, robot, ai):
        # TODO: just delete the image and reclassify the robot as a
        # real robot
        #del robot
        pass

    def initAI(self):
        logging.debug("Initialising AI")

        ai1, real1 = self.robot1
        ai2, real2 = self.robot2

        if ai1 and real1:
            real_interface = RealRobotInterface()
            #meta_interface = MetaInterface(real_interface, self.robots[0])
            ai = ai1(self.world, real_interface)
            self.ai.append(ai)
            robotSprite = self.robots[0]
            #self.robots[0] = ai
            #del robotSprite
            self.setRobotAI(self.robots[0], ai)
            logging.debug("AI 1 started in the real world")
        elif ai1:
            self.ai.append( ai1(self.world, self.robots[0]) )
            logging.debug("AI 1 started in the simulated world")
        else:
            logging.debug("No AI 1 present")

        if ai2 and real2:
            # TODO: reverse sides here
            ai = ai2(self.world, RealRobotInterface())
            self.ai.append(ai)
            robotSprite = self.robots[0]
            self.robots[1] = ai
            #del robotSprite
            self.setRobotAI(self.robots[1], ai)
            logging.debug("AI 2 started in the real world")
        elif ai2:
            self.ai.append( ai2(self.world, self.robots[1]) )
            logging.debug("AI 2 started in the simulated world")
        else:
            logging.debug("No AI 2 present")

    def runAI(self):
        #logging.debug("Running AI players")
        for ai in self.ai:
            ai.run()

    def run(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.initVision()
        self.initScreen()
        self.loadImages()
        self.makeObjects()
        self.world.assignSides()
        self.initAI()
        self.initInput()
        # by initialising the input after the AI, we can control even
        # AI robots with keyboard
        self.drawEnts()

        while True:
            self.handleInput()
            self.clock.tick(25)
            self.drawEnts()
            self.sprites.update()
            self.runAI()

    def initInput(self):
        self.input = Input(self, self.robots[0], self.robots[1])

    def handleInput(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            else:
                #logging.debug("Got input event: %s", event)
                self.input.robotInput(event)

    def makeRobot(self, pos, colour, angle, ai):
        ent = Robot(self, pos, self.images[colour], angle)
        ent.side = colour

        self.world.ents[colour] = ent
        self.robots.append(ent)
        self.addEnt(ent)

    def makeBall(self, pos):
        ent = Ball(self, pos, self.images['ball'])
        #ent.v += [1, 7]
        self.world.ents['ball'] = ent
        self.addEnt(ent)

    def addEnt(self, ent):
        self.objects.append(ent)

    def loadImages(self):
        logging.debug("Loading images")
        for name in World.image_names.keys():
            self.images[name] = pygame.image.load(World.image_names[name])

if __name__ == '__main__':
    sim = Simulator()
    sim.run()


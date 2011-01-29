#! /usr/bin/env python
# -*- coding: utf-8 -*-

from common.utils import *
from math import *
from pygame.locals import *
from random import *
import numpy as np
import pygame
import sys, logging

class Visualiser(object):
    """A rudimentary visualisation tool for movement trajectories.

    This is an incomplete tool for getting some intuitions about how
    to program the robot. Sometimes it's better to use straight-line
    movement, other times it's better to move in an arc.
    """

    headless = False
    worldDim = np.array((2240.0, 1215.0))
    resolution = np.array( map(int, worldDim/6) )
    robotSize = np.array((200.0, 200.0))
    startDim = np.array( map(int, robotSize/worldDim * resolution) )
    speed = 20 # mm/s
    max_speed = 100 # mm/s
    turn_speed = 0.03 # radians/s
    max_turn_speed = 1.0 # radians/s

    def __init__(self):
        self.screen = None
        self.reset()

    def reset(self):
        self.startOrient = 0
        self.obstacleOrient = 0
        self.startPos = None
        self.goalPos = None
        self.obstacles = []
        self.showNPF = False
        if self.screen:
            self.screen.fill( (0,0,0,0) )

    def initScreen(self):
        logging.debug("Creating screen")
        if self.headless:
            self.screen = pygame.Surface(self.resolution)
        else:
            pygame.display.set_mode(self.resolution)
            pygame.display.set_caption('SDP 9 movement visualiser')
            self.screen = pygame.display.get_surface()

    def NPF(self):
        R = (self.speed / self.turn_speed) * \
            self.resolution[0]/self.worldDim[0]

        """
        For tangent line passing through (x1,y1):

        Left circle (centered at (-R,0)):
        (x1 + R)(x + R) + y*y1 = R^2
        R^2 + R*(x+x1) + x*x1 + y*y1 = R^2
        R*(x+x1) + x*x1 + y*y1 = 0
        (1+R)*(x+x1) + y*y1 = 0

        Right circle (centered at (R,0)):
        (x1 - R)(x - R) + y*y1 = R^2
        R^2 - R*(x+x1) + x*x1 + y*y1 = R^2
        -R*(x+x1) + x*x1 + y*y1 = 0
        (1-R)*(x+x1) + y*y1 = 0
        """

        inf = 1e1000
        # Switch to a self-centric view
        points = rotatePoints( [(x,y) for x in range(self.resolution[0])
                                     for y in range(self.resolution[1])],
                              self.startPos, -self.startOrient, new_origin=True )

        offset = self.resolution/2
        #self.startPos = np.array(rotatePoints([self.startPos], self.startPos, -self.startOrient)[0]) + offset
        self.startPos = np.array([1,1]) + offset
        self.startOrient = 0
        self.goalPos = np.array(rotatePoints([self.goalPos], self.startPos, -self.startOrient)[0]) + offset
        self.obstacles = map(lambda x: np.array(x)+offset,
                             rotatePoints(self.obstacles, self.startPos,
                                          -self.startOrient))

        self.screen.fill( (0,0,0,0) )
        Max = 0

        for x,y in points:
            """
            First evaluate whether a target point (x1,y1) is within a
            circle of inaccessibility:

            if (x1 ± R)^2 + y1^2 < R^2, set dist = Inf,
            <=> R^2 ± 2R*x1 + x1^2 + y1^2 < R^2,
            <=> x1^2 + y1^2 ± 2R*x1 < 0,
            <=> x1^2 + y1^2 < ± 2R*x1.
            <=> x1^2 + y1^2 < 2R*|x1|.
            """
            if x**2 + y**2 < 2*R*abs(y):
                dist = inf

            """
            Otherwise,
            use the tangent equations above to find the closest point on a
            circle and set dist = dist(p2, p1) + length travelled along circle.

            From http://mathworld.wolfram.com/Circle-LineIntersection.html

            Since we only care about tangent intersections, we
            simplify the equations:
            """
            x1, x2 = 0, x
            y1, y2 = R, y
            dx = x2 - x1
            dy = y2 - y1
            dt = sqrt(dx**2 + dy**2)
            Det = x1*y2 - x2*y1
            x_i =  Det*dy / dt**2
            y_i = -Det*dx / dt**2

            # TODO: same for the other circle; use the smaller value
            tangent_dist = sqrt( (x_i-x)**2 + (y_i-y)**2 )
            # TODO: either use this or pi - this depending on circle side
            angle = atan2(y_i/R, x_i/R)
            circle_walk_dist = R*angle/pi
            dist = tangent_dist + circle_walk_dist

            # for o in self.obstacles:
            #     dist += ( (x_i-o[0])**2 + (y_i-o[1])**2 )** -0.1
            # g = self.goalPos
            # dist -= sqrt( (x_i-g[0])**2 + (y_i-g[1])**2 )

            "The straight line distance"
            angle1 = atan2(y, x)
            if -pi/2 <= angle1 <= pi/2:
                angle2 = abs(angle1)
            else:
                angle2 = pi - abs(angle1)

            dist2 = self.turn_speed/pi * self.speed * angle2 \
                + sqrt(x**2 + y**2)

            col = [0, min(255, max(0, int(200 - dist))), 0]
            if dist > Max: Max = dist

            if dist2 < dist:
                col = [min(255, max(0, int(200 - dist2))), 0, 0]

            self.screen.set_at(offset + map(int, (x,y)), col)

        print "DONE", Max
        #self.showNPF = False

    def run(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.initScreen()
        self.screen.blit(self.screen, (0,0))
        while True:
            self.clock.tick(100)
            self.handleInput()
            if self.goalPos is not None and self.showNPF:
                self.NPF()
            self.drawStart()
            self.drawStartOrient()
            self.drawGoal()
            self.drawObstacle()
            pygame.display.flip()

    def drawStart(self):
        if self.startPos is None: return
        pygame.draw.circle(self.screen, (0,0,128,0), self.startPos,
                           self.startDim[0]/2)

    def drawStartOrient(self):
        if self.startOrient is None or self.startPos is None: return
        R = self.startDim[0]/2
        pygame.draw.line(self.screen, (150,0,128,0), self.startPos,
                         ( self.startPos[0]+R*cos(self.startOrient),
                           self.startPos[1]+R*sin(self.startOrient)),2)

    def drawGoal(self):
        if self.goalPos is None: return
        pygame.draw.circle(self.screen, (255,0,0,0), self.goalPos, 10)

    def drawObstacle(self):
        for obs in self.obstacles:
            pygame.draw.circle(self.screen, (180,180,40,0), obs, 20)

    def handleInput(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            if event.type == KEYDOWN:
                if event.key == K_r:
                    self.reset()
                elif event.key == K_d:
                    self.showNPF = not self.showNPF
            elif event.type == MOUSEBUTTONDOWN:
                pos = event.pos
                if event.button == 1:
                    if self.startPos is None:
                        print "START"
                        self.startPos = pos
                    elif not self.startOrient:
                        self.startOrient = atan2(pos[1] - self.startPos[1],
                                                 pos[0] - self.startPos[0])
                    elif self.goalPos is None:
                        print "GOAL"
                        self.goalPos = pos
                    else:
                        print "OBSTACLE"
                        self.obstacles.append(pos)

                elif event.button == 3:
                    self.speed = \
                        pos[0]/float(self.resolution[0]) * self.max_speed
                    self.turn_speed = \
                        pos[1]/float(self.resolution[1]) * self.max_turn_speed

                    print "Speed: %.1f mm/s  Turn speed: %.4f rad/s" \
                        % (self.speed, self.turn_speed)

                #logging.debug("Got input event: %s", event)

if __name__ == '__main__':
    vis = Visualiser()
    vis.run()


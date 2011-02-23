#! /usr/bin/env python
# -*- coding: utf-8 -*-

from common.utils import *
from communication.robot_interface2 import *
from copy import copy
from strategy.strategy import Strategy
from input import Input
from math import *
from pygame.color import THECOLORS
from pygame.locals import *
from random import *
from robot import Robot
from world import World
import common.world
import pygame, pymunk
import numpy as np
import sys, logging
from strategy.apf import *

class Simulator(object):

    tickrate = 25.0
    speed = 2
    scale = 3 # pixel/cm
    offset = 4.0
    Resolution = map( int, scale*(2*offset+np.array([World.PitchLength,
                                                    World.PitchWidth])) )

    # Options and arguments
    headless=False
    ai=[]
    robot1=None
    robot2=None

    apf_scale = 0.1*scale
    apf_dist = 60*scale

    def __init__(self, **kwargs):
        self.log = logging.getLogger("simulator2")
        self.log.debug("Simulator started with the arguments:")
        for k, v in kwargs.items():
            self.__setattr__(k, v)
            self.log.debug("\t%s = %s", k, v)

        self.prev = {}
        self.robots=[]

    def convertPos(self, pos):
        return pos
        return map(lambda x:self.scale*(x+self.offset), pos)
    def convertVel(self, vel):
        return vel
        return map(lambda x:x*self.scale, vel)

    def set_state(self, state):
        R = state.robot
        self.prev['robot'] = {'pos':self.convertPos([R.pos_x, R.pos_y]),
                              'vel':self.convertVel([R.vel_x, R.vel_y]),
                              'ang_v':R.ang_v,
                              'angle':R.angle,
                              'left_angle':R.left_angle,
                              'right_angle':R.right_angle,
                              }

        B = state.ball
        self.prev['ball'] = {'pos':self.convertPos([B.pos_x, B.pos_y]),
                              'vel':self.convertVel([B.vel_x, B.vel_y]),
                              'ang_v':B.ang_v,
                              }

        self.goal = state.target

        self.load_state()

    def save_state(self):
        ball = self.world.getBall()
        self.prev['ball'] = {'pos':list(ball.pos),
                             'vel':list(bal.velocity),
                             'ang_v':ball.ang_v,
                             }


        robot = self.world.getSelf()
        self.prev['robot'] = {'pos':list(robot.pos),
                              'vel':list(robot.velocity),
                              'ang_v':robot.ang_v,
                              'angle':robot.orientation,
                              'left_angle':robot.left_angle,
                              'right_angle':robot.right_angle,
                              }

    def load_state(self):
        self.ball.body.position = pymunk.Vec2d(self.prev['ball']['pos'])
        self.ball.body.velocity = pymunk.Vec2d(self.prev['ball']['vel'])
        self.ball.body.angular_velocity = self.prev['ball']['ang_v']

        self.robots[0].robot.body.position = pymunk.Vec2d(self.prev['robot']['pos'])
        self.robots[0].robot.body.velocity = pymunk.Vec2d(self.prev['robot']['vel'])
        self.robots[0].robot.body.angular_velocity = self.prev['robot']['ang_v']
        self.robots[0].robot.body.angle = self.prev['robot']['angle']
        self.robots[0].wheel_left.body.angle = self.prev['robot']['left_angle']
        self.robots[0].wheel_right.body.angle = self.prev['robot']['right_angle']

        self.robots[0].wheel_left.body.position = self.robots[0].left_wheel_pos()
        self.robots[0].wheel_right.body.position = self.robots[0].right_wheel_pos()
        self.robots[0].stop_steer()

    def init_physics(self):
	pymunk.init_pymunk()
	self.space = pymunk.Space()
	self.space.gravity = (0,0)

    def draw_ents(self):
        if self.headless:
            return

        pygame.display.set_caption( "FPS: %.1f" % self.clock.get_fps() )

        self.screen.blit(self.overlay, (0,0))

        self.draw_field()
        self.draw_walls()
        self.draw_ball()
        # Draw the robots
        try:
            map(lambda x: x.draw(), self.robots)
        except:
            pass

    def init_screen(self):
        self.log.debug("Creating simulator screen")
        self.world.setResolution(self.Resolution)
        if self.headless:
            self.screen = pygame.Surface(self.Resolution)
        else:
            pygame.display.set_mode(self.Resolution)
            pygame.display.set_caption('SDP 9 Simulator')
            self.screen = pygame.display.get_surface()
            self.overlay = pygame.Surface(self.Resolution)
            self.overlay.fill((130,130,130,255))

    def make_objects(self):
        self.log.debug("Creating game objects")

	self.walls = self.add_walls(self.space)
	self.ball = self.add_ball(self.space)

        colours = ('blue', 'yellow')
        if random() < 0.5:
            col1, col2 = colours
        else:
            col2, col1 = colours

        self.log.info("Robot 1 is %s. Robot 2 is %s", col1, col2)
        pos1 = self.scale * pymunk.Vec2d( (World.PitchLength/2.0 - 60,
                                           World.PitchWidth/2.0 + self.offset) )
        pos2 = self.scale * pymunk.Vec2d( (World.PitchLength/2.0 + 60,
                                           World.PitchWidth/2.0 + self.offset) )
        self.make_robot(pos1, col1, 0, self.robot1[0])
        #self.make_robot(pos2, col2, -pi, self.robot2[0])

        self.world.setSelf(self.robots[0])
        self.world.setBall(self.ball)

    def init_AI(self):
        self.log.debug("Initialising AI")

        ai1, real1 = self.robot1
        ai2, real2 = self.robot2

        if ai1 and real1:
            real_interface = RealRobotInterface()
            #meta_interface = MetaInterface(real_interface, self.robots[0])
            ai = ai1(self.world, real_interface)
            self.ai.append(ai)
            #robotSprite = self.robots[0]
            self.robots[0] = ai
            #self.setRobotAI(self.robots[0], ai)
            self.log.debug("AI 1 started in the real world")
        elif ai1:
            self.ai.append( ai1(self.world, self.robots[0], self.ai_args[0], self) )
            self.log.debug("AI 1 started in the simulated world")
        else:
            self.log.debug("No AI 1 present")

        if ai2 and real2:
            # TODO: reverse sides here
            ai = ai2(self.world, RealRobotInterface())
            self.ai.append(ai)
            robotSprite = self.robots[0]
            self.robots[1] = ai
            #del robotSprite
            self.setRobotAI(self.robots[1], ai)
            self.log.debug("AI 2 started in the real world")
        elif ai2:
            self.ai.append( ai2(self.world, self.robots[1]) )
            self.log.debug("AI 2 started in the simulated world")
        else:
            self.log.debug("No AI 2 present")

    def runAI(self):
        #self.log.debug("Running AI players")
        for ai in self.ai:
            ai.run()
            ai.sendMessage()

    def timestep(self):
        self.space.step(1/self.tickrate)
        map(lambda x:x.tick(), self.robots)
        self.ball.body.velocity *= 0.997

    def update_objects(self):
        for _ in range(self.speed):
            self.timestep()

        if self.ball.body.position.x < 0 \
                or self.ball.body.position.y < 0 \
                or self.ball.body.position.x > self.Resolution[0] \
                or self.ball.body.position.y > self.Resolution[1]:

            self.ball.body.position = pymunk.Vec2d(self.Resolution[0]/2.0,
                                                   self.Resolution[1]/2.0)

    def run(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.init_physics()
        self.init_screen()
        self.make_objects()
        self.world.assignSides()
        self.init_AI()
        self.init_input()
        # by initialising the input after the AI, we can control even
        # AI robots with keyboard

        while True:
            self.clock.tick(self.tickrate)
            self.handle_input()
            self.update_objects()
            self.draw_ents()
            self.runAI()
            pygame.display.flip()

    def init_input(self):
        self.input = Input(self, self.robots[0], self.robots[0]) #self.robots[1])

    def handle_input(self):
        if self.headless:
            return
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            self.input.robotInput(event)

    def make_robot(self, pos, colour, angle, ai):
        robot = Robot(pos, colour, self)
        self.world.ents[colour] = robot
        self.robots.append(robot)

    def add_walls(self, space):
        body = pymunk.Body(pymunk.inf, pymunk.inf)

        offset = self.offset
        goal_corner = offset + World.PitchWidth/2.0 - World.GoalLength/2.0
        goal_corner2 = goal_corner + World.GoalLength
        y_corner = offset + World.PitchWidth
        x_corner = offset + World.PitchLength
        x_corner2 = 2*offset + World.PitchLength

        lines = [  ((offset, offset), (offset, goal_corner))
                  ,((offset, goal_corner), (0, goal_corner))
                  ,((0, goal_corner), (0, goal_corner2))
                  ,((0, goal_corner2), (offset, goal_corner2))
                  ,((offset, goal_corner2), (offset, y_corner))
                  ,((offset, y_corner), (x_corner, y_corner))
                  ,((x_corner, y_corner), (x_corner, goal_corner2))
                  ,((x_corner, goal_corner2), (x_corner2, goal_corner2))
                  ,((x_corner2, goal_corner2), (x_corner2, goal_corner))
                  ,((x_corner2, goal_corner), (x_corner, goal_corner))
                  ,((x_corner, goal_corner), (x_corner, offset))
                  ,((x_corner, offset), (offset, offset))
                  ]

        def rescale(point):
            return (self.scale*point[0], self.scale*point[1])
        def get_static_line((p1,p2)):
            return pymunk.Segment(body, rescale(p1), rescale(p2), 1.0)
        static_lines = map(get_static_line, lines)

        for line in static_lines:
            line.elasticity = 0.75
            line.group = 1
        space.add_static(static_lines)
        return static_lines

    def draw_walls(self):
    	for line in self.walls:
            body = line.body
            pv1 = body.position + line.a.rotated(body.angle)
            pv2 = body.position + line.b.rotated(body.angle)
            pygame.draw.lines(self.screen,
                              THECOLORS["black"], False, [pv1,pv2])

    def add_ball(self, space):
	mass = 1
    	radius = 5
	inertia = pymunk.moment_for_circle(mass, 0.999, radius)
    	body = pymunk.Body(mass, inertia)
    	body.position = self.offset + self.scale/2.0 * \
            pymunk.Vec2d(World.PitchLength, World.PitchWidth)
    	shape = pymunk.Circle(body, radius)
	shape.elasticity = 0.6
	#shape.friction = 1
    	shape.group = 3
    	space.add(body, shape)
    	return shape

    def draw_field(self):
    	ball = map(int, self.ball.body.position)
        offset = 4000
        X = range(max(0,ball[0]-offset), min(self.Resolution[0],ball[0]+offset), 30)
        Y = range(max(0,ball[1]-offset), min(self.Resolution[1],ball[1]+offset), 30)

        goal = self.offset+self.scale*World.PitchLength, \
            self.offset+self.scale*World.PitchWidth/2.0

        def pf(pos):
            return all_apf( pos, self.Resolution, ball, goal, World.BallRadius )
            return tangential_field(1, ball, pos, self.apf_scale, self.apf_dist)
            return attractive_field( ball, pos, self.apf_scale, self.apf_dist )

        for x in X:
            for y in Y:
                pos = x,y
                v = pf(pos)
                delta = map(lambda x:int(round(x)), (pos[0]+v[0], pos[1]+v[1]))
                if delta != map(lambda x:int(round(x)), pos):
                    pygame.draw.line(self.screen, THECOLORS['yellow'], pos, delta, 1)
                    pygame.draw.circle(self.screen, THECOLORS['orange'], delta, 1)


    def draw_ball(self):
    	pos = map(int, self.ball.body.position)
    	pygame.draw.circle( self.screen, THECOLORS["red"], pos,
                            int(self.scale * World.BallDiameter/2.0) )

if __name__ == '__main__':
	sys.exit(main())

#! /usr/bin/env python
# -*- coding: utf-8 -*-

from common.utils import *
from communication.client import *
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
import pygame
import pymunk
import sys, logging

class Simulator(object):

    # Options and arguments
    headless=False
    ai=[]
    robot1=None
    robot2=None

    scale = 3 # pixel/cm
    offset = 4.0
    Resolution = map( int, scale*(2*offset+np.array([World.PitchLength,
                                                    World.PitchWidth])) )

    def __init__(self, **kwargs):
        self.log = logging.getLogger("simulator2")
        self.log.debug("Simulator started with the arguments:")
        for k, v in kwargs.items():
            self.__setattr__(k, v)
            self.log.debug("\t%s = %s", k, v)

        self.robots=[]

    def set_state(state):
        R = state.robot
        self.prev['robot'] = {'pos':[R.pos_x, R.pos_y],
                              'vel':[R.vel_x, R.vel_y],
                              'ang_v':R.ang_v,
                              'angle':R.angle,
                              'left_angle':R.left_angle,
                              'right_angle':R.right_angle,
                              }

        B = state.ball
        self.prev['ball'] = {'pos':[B.ball_x, B.ball_y],
                              'vel':[B.ball_vx, B.ball_vy],
                              'ang_v':B.ang_v,
                              }

        self.load_state()

    def save_state(self):
        self.prev = {}
        self.prev['ball'] = {'pos':list(self.ball.body.position),
                             'vel':list(self.ball.body.velocity),
                             'ang_v':self.ball.body.angular_velocity
                             }
        self.prev['robot'] = {'pos':list(self.robots[0].robot.body.position),
                              'vel':list(self.robots[0].robot.body.velocity),
                              'ang_v':self.robots[0].robot.body.angular_velocity,
                              'angle':self.robots[0].robot.body.angle,
                              'left_angle':self.robots[0].wheel_left.body.angle,
                              'right_angle':self.robots[0].wheel_right.body.angle,
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

    def init_physics(self):
	pymunk.init_pymunk()
	self.space = pymunk.Space()
	self.space.gravity = (0,0)
	#space.damping = 0.6

	### Adding the object to the space
	self.walls = self.add_walls(self.space)
	self.ball = self.add_ball(self.space)

    def draw_ents(self):
        pygame.display.set_caption( "FPS: %.1f" % self.clock.get_fps() )

        self.draw_walls()
        self.draw_ball()
        # Draw the robots
        map(lambda x: x.draw(), self.robots)

        self.screen.blit(self.overlay, (0,0))
        self.overlay.fill((130,130,130,255))
        if not self.headless:
            pygame.display.flip()

    def init_screen(self):
        self.log.debug("Creating simulator screen")
        if self.headless:
            self.screen = pygame.Surface(self.Resolution)
        else:
            pygame.display.set_mode(self.Resolution)
            pygame.display.set_caption('SDP 9 Simulator')
            self.screen = pygame.display.get_surface()
            self.overlay = pygame.Surface(self.Resolution)
            self.overlay.convert_alpha()
            self.overlay.set_alpha(100)

    def make_objects(self):
        self.log.debug("Creating game objects")

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
            robotSprite = self.robots[0]
            self.robots[0] = ai
            self.setRobotAI(self.robots[0], ai)
            self.log.debug("AI 1 started in the real world")
        elif ai1:
            self.ai.append( ai1(self.world, self.robots[0], self) )
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

    def update_objects(self):
        self.space.step(1/self.tickrate)
        map(lambda x:x.tick(), self.robots)
        self.ball.body.velocity.x /= 1.007
        self.ball.body.velocity.y /= 1.007

    def run(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.tickrate = 50.0
        self.init_physics()
        self.init_screen()
        self.make_objects()
        self.world.assignSides()
        self.init_AI()
        self.init_input()
        # by initialising the input after the AI, we can control even
        # AI robots with keyboard
        self.draw_ents()

        while True:
            self.clock.tick(self.tickrate)
            self.handle_input()
            self.update_objects()
            self.draw_ents()
            self.runAI()

    def init_input(self):
        self.input = Input(self, self.robots[0], self.robots[0]) #self.robots[1])

    def handle_input(self):
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
            line.elasticity = 0.3
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
    	inertia = pymunk.moment_for_circle(mass, 0, radius)
    	body = pymunk.Body(mass, inertia)
    	body.position = self.offset + self.scale/2.0 * \
            pymunk.Vec2d(World.PitchLength, World.PitchWidth)
    	shape = pymunk.Circle(body, radius)
    	shape.elasticity = 0.1
    	shape.friction = 0.9
    	shape.group = 3
    	space.add(body, shape)
    	return shape

    def draw_ball(self):
    	pos = int(self.ball.body.position.x), int(self.ball.body.position.y)
    	pygame.draw.circle( self.screen, THECOLORS["red"], pos,
                            int(self.scale * World.BallDiameter/2.0) )

if __name__ == '__main__':
	sys.exit(main())

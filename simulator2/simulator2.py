#! /usr/bin/env python
# -*- coding: utf-8 -*-

from common.utils import *
from communication.client import *
from strategy.strategy import Strategy
from ball import *
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
    pitch=None
    ai=[]
    robot1=None
    robot2=None

    scale = 3 # pixel/cm
    offset = 4.0
    Resolution = map( int, scale*(2*offset+np.array([World.PitchLength,
                                                    World.PitchWidth])) )

    def __init__(self, **kwargs):
        logging.debug("Simulator started with the arguments:")
        for k, v in kwargs.items():
            self.__setattr__(k, v)
            logging.debug("\t%s = %s", k, v)

        self.robots=[]

    def init_physics(self):
	pymunk.init_pymunk()
	self.space = pymunk.Space()
	self.space.gravity = (0,0)
	#space.damping = 0.6

	### Adding the object to the space
	self.walls = self.add_walls(self.space)
	self.ball = self.add_ball(self.space)

	### Initialisation of the robot
	self.us = self.add_robot(self.space)
	self.kickZone = self.kick_bounding_box(self.space, self.us)
	self.wheel1 = self.add_wheel_right(self.space, self.us)
	self.wheel2 = self.add_wheel_left(self.space, self.us)
	self.us.body.position = (100,100)
	self.wheel1.body.position = (115, 85)
	self.wheel2.body.position = (85, 115)
	self.cons1 = pymunk.SimpleMotor(self.us.body, self.wheel1.body, 0)
	self.cons2 = pymunk.SimpleMotor(self.us.body, self.wheel2.body, 0)
	self.space.add(self.cons1, self.cons2)

    def draw_ents(self):
        pygame.display.set_caption("fps: " + str(self.clock.get_fps()))

        self.draw_walls()
        self.draw_ball()
        self.draw_robot(self.us)
        self.draw_wheel(self.wheel1)
        self.draw_wheel(self.wheel2)
        self.draw_kick_zone(self.kickZone)

        map(lambda x: x.draw(), self.robots)

        # Update overlay after we've passed the "raw image" to vision
        self.screen.blit(self.overlay, (0,0))
        # Make the overlay "blank" again. Should be completely
        # transparent but I don't know how to do that
        self.overlay.fill( (130,130,130,255))
        if not self.headless:
            pygame.display.flip()

    def init_screen(self):
        logging.debug("Creating simulator screen")
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
        logging.debug("Creating game objects")

        colours = ('blue', 'yellow')
        if random() < 0.5:
            col1, col2 = colours
        else:
            col2, col1 = colours

        logging.info("Robot 1 is %s. Robot 2 is %s", col1, col2)
        pos1 = self.scale * pymunk.Vec2d( (World.PitchLength/2.0 - 60,
                                           World.PitchWidth/2.0 + self.offset) )
        pos2 = self.scale * pymunk.Vec2d( (World.PitchLength/2.0 + 60,
                                           World.PitchWidth/2.0 + self.offset) )
        self.make_robot(pos1, col1, 0, self.robot1[0])
        self.make_robot(pos2, col2, -pi, self.robot2[0])

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

    def update_objects(self):
        self.space.step(1/self.tickrate)
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
        self.initAI()
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
        #self.input = Input(self, self.robots[0], self.robots[1])
        pass

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            if event.type == KEYDOWN and event.key == K_s:
                stop(self.us, self.wheel1, self.wheel2)
            elif event.type == KEYDOWN and event.key == K_a:
                self.wheel1.body.angle -= radians(5)
                self.wheel2.body.angle -= radians(5)
            elif event.type == KEYDOWN and event.key == K_d:
                self.wheel1.body.angle += radians(5)
                self.wheel2.body.angle += radians(5)
            elif event.type == KEYDOWN and event.key == K_r:
                reset(self.us, self.wheel1, self.wheel2)
            elif event.type == KEYDOWN and event.key == K_SPACE:
                kick(self.us, self.ball, self.kickZone)
            elif event.type == KEYDOWN and event.key == K_w:
                drive(self.wheel1, self.wheel2)
            elif event.type == KEYDOWN and event.key == K_c:
                startSpinRight(self.us, self.wheel1, self.wheel2)
            elif event.type == KEYDOWN and event.key == K_z:
                startSpinLeft(self.us, self.wheel1, self.wheel2)
            elif event.type == KEYDOWN and event.key == K_x:
                stopSpin(self.us, self.wheel1, self.wheel2)

    def make_robot(self, pos, colour, angle, ai):
        robot = Robot(pos, colour, self.space, self.scale, self.screen)
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
                   #,((0, goal_corner), (0, goal_corner2))
                  ,((0, goal_corner2), (offset, goal_corner2))
                  ,((offset, goal_corner2), (offset, y_corner))
                  ,((offset, y_corner), (x_corner, y_corner))
                  ,((x_corner, y_corner), (x_corner, goal_corner2))
                  ,((x_corner, goal_corner2), (x_corner2, goal_corner2))
                  #,((x_corner2, goal_corner2), (x_corner2, goal_corner))
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
    	body.position = 384,212
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

    def add_robot(self, space):
    	fp=[]; _fp = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        for x,y in _fp:
            fp.append( (self.scale*x*World.RobotLength/2.0,
                        self.scale*y*World.RobotWidth/2.0) )

    	mass = 	1000
    	moment = pymunk.moment_for_poly(mass, fp)
    	robot_body = pymunk.Body(mass, moment)

    	robot_shape = pymunk.Poly(robot_body, fp)
    	robot_shape.friction = 0.99
    	robot_shape.group = 2
    	space.add(robot_body, robot_shape)

    	return robot_shape

    def draw_robot(self, robot):
    	### draw lines around the robot
    	ps = robot.get_points()
    	ps.append(ps[0])
    	pygame.draw.lines(self.screen, THECOLORS["blue"], False, ps, 4)

    def add_wheel(self, space, robot, pos):
        wdist = 4.0 # Wheel distance from body center
        fp = [(-3, -1), (3, -1), (3, 1), (-3, 1)]
        mass = 1000
        moment = pymunk.moment_for_poly(mass, fp)
        wheel_body = pymunk.Body(mass, moment)
        wheel_shape = pymunk.Poly(wheel_body, fp)
        wheel_shape.group = 2
    	wheel_body.position = (robot.body.position[0] + self.scale*wdist*pos[0],
                               robot.body.position[1] + self.scale*wdist*pos[1])
    	joint = pymunk.PivotJoint(robot.body, wheel_body, wheel_body.position)
        space.add(wheel_body, wheel_shape, joint)
        return wheel_shape

    def add_wheel_right(self, space, robot):
        return self.add_wheel(space, robot, (1, -1))

    def add_wheel_left(self, space, robot):
        return self.add_wheel(space, robot, (-1, 1))

    def draw_wheel(self, wheel):
        ps = wheel.get_points()
        ps.append(ps[0])
        pygame.draw.lines(self.screen, THECOLORS["black"], False, ps, 5)

    def kick_bounding_box(self, space, robot):
    	p = robot.get_points()
    	bb = []
    	bb.append((p[1][0], p[1][1]) )
    	bb.append( (p[1][0]+10*cos(robot.body.angle),
                    p[1][1]+10*sin(robot.body.angle)) )
    	bb.append( (p[2][0]+10*cos(robot.body.angle),
                    p[2][1]+10*sin(robot.body.angle)) )
    	bb.append((p[2][0], p[2][1]) )
    	shape = pymunk.Poly(robot.body, bb)
    	shape.group = 3
    	space.add(shape)
    	return shape

    def draw_kick_zone(self, zone):
    	ps = zone.get_points()
    	pygame.draw.lines(self.screen, THECOLORS["red"], False, ps, 3)


def reset(robot, wheel1, wheel2):
	wheel1.body.angle = robot.body.angle
	wheel2.body.angle = robot.body.angle


## Robot commands
def steer_angle_left(angle):
        angle = radians(angle)

def steer_angle_right(angle):
        angle = radians(angle)

wheel_max_v = 100
def drive_left(speed):
	max_v =  (wheel_max_v * cos(wheel1.body.angle),
                  wheel_max_v * sin(wheel1.body.angle))
	# wheel1.body.velocity =  (wheel_max_v * cos(wheel1.body.angle),
        #                          wheel_max_v * sin(wheel1.body.angle))

def drive_right(speed):
        pass

def kick(robot, ball, kickZone):
	if kickZone.point_query(ball.body.position):
		ball.body.apply_impulse((100*cos(robot.body.angle), 100*sin(robot.body.angle)), (0,0))

def reset():
        pass

## Old-style commands
def drive(wheel1, wheel2):
	wheel1.body.velocity =  (100*cos(wheel1.body.angle), 100*sin(wheel1.body.angle))
	wheel2.body.velocity =  (100*cos(wheel2.body.angle), 100*sin(wheel2.body.angle))

def stop(robot, wheel1, wheel2):
	wheel1.body.velocity = (0, 0)
	wheel2.body.velocity = (0, 0)
	robot.body.velocity = (0, 0)
	robot.body.angular_velocity = 0
	wheel1.body.angular_velocity = 0
	wheel2.body.angular_velocity = 0

def startSpinRight(robot, wheel1, wheel2):
	wheel1.body.angle = robot.body.angle + pi/4
	wheel2.body.angle = robot.body.angle - 3*pi/4

def startSpinLeft(robot, wheel1, wheel2):
	wheel1.body.angle = robot.body.angle - 3*pi/4
	wheel2.body.angle = robot.body.angle + pi/4

	# wheel1.body.angle = robot.body.angle + 3*pi/4
	# wheel2.body.angle = robot.body.angle - pi/4

def stopSpin(robot, wheel1, wheel2):
	robot.angular_velocity = 0
	wheel1.angular_velocity = 0
	wheel2.angular_velocity = 0
	reset(robot, wheel1, wheel2)
	stop(robot, wheel1, wheel2)

def setRobotDirection(robot, wheel1, wheel2, angle):
	wheel1.body.angle = robot.body.angle + radians(angle)
	wheel2.body.angle = robot.body.angle + radians(angle)

def turnLeftWheelByAmount(wheel, amount):
	wheel.body.angle += radians(amount)

def turnRightWheelByAmount(wheel, amount):
	wheel.body.angle += radians(amount)

def turnLeftWheelTo(robot, wheel, angle):
	wheel.body.angle = robot.body.angle + radians(angle)

def turnRightWheelTo(robot, wheel, angle):
	wheel.body.angle = robot.body.angle + radians(angle)

if __name__ == '__main__':
	sys.exit(main())

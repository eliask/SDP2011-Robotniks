from common.utils import *
from copy import deepcopy
from math import *
from pygame.color import THECOLORS
from pygame.locals import *
from random import *
from robot_interface import *
from world import World
import logging
import pygame, pymunk
import pygame.gfxdraw

class Robot(SimRobotInterface):

    def __init__(self, pos, colour, sim):
        self.sim = sim
        self.colour = colour

        space = self.sim.space
	self.robot = self.add_robot(space, pos)
	self.kickzone = self.add_kickzone(space)
	self.wheel_left  = self.add_wheel_left(space)
	self.wheel_right = self.add_wheel_right(space)

	self.cons1 = pymunk.SimpleMotor(self.robot.body,
                                        self.wheel_left.body, 0)
	self.cons2 = pymunk.SimpleMotor(self.robot.body,
                                        self.wheel_right.body, 0)
	space.add(self.cons1, self.cons2)

        SimRobotInterface.__init__(self)

    def add_robot(self, space, pos):
    	fp=[]; _fp = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        for x,y in _fp:
            fp.append( (self.sim.scale*x*World.RobotLength/2.0,
                        self.sim.scale*y*World.RobotWidth/2.0) )

    	mass = 	1000
    	moment = pymunk.moment_for_poly(mass, fp)
    	robot_body = pymunk.Body(mass, moment)
        robot_body.position = pos

    	robot_shape = pymunk.Poly(robot_body, fp)
	robot_shape.friction = 0.8
    	robot_shape.group = 2
    	space.add(robot_body, robot_shape)
        return robot_shape

    def wheel_pos(self, _wpos):
        angle = self.robot.body.angle
        wpos = pymunk.Vec2d(*_wpos)
        wpos.rotate(angle)
        wdist = 4.0 # Wheel distance from body center (cm)
        pos = self.robot.body.position + self.sim.scale*wdist*wpos
        return pos

    def left_wheel_pos(self):
        return self.wheel_pos((-1, -1))
    def right_wheel_pos(self):
        return self.wheel_pos((1, 1))

    def add_wheel(self, space, pos):
        fp = [(-5, -3), (5, -3), (5, 3), (-5, 3)]
        mass = 1000
        moment = pymunk.moment_for_poly(mass, fp)
        wheel_body = pymunk.Body(mass, moment)
        wheel_shape = pymunk.Poly(wheel_body, fp)
        wheel_shape.group = 2
	wheel_body.position = pos
    	joint = pymunk.PivotJoint(self.robot.body, wheel_body, wheel_body.position)
        space.add(wheel_body, wheel_shape, joint)
        return wheel_shape

    def add_wheel_left(self, space):
        return self.add_wheel(space, self.left_wheel_pos())

    def add_wheel_right(self, space):
        return self.add_wheel(space, self.right_wheel_pos())

    def add_kickzone(self, space):
    	bb = self.get_kicker_points()
    	shape = pymunk.Poly(self.robot.body, bb)
    	shape.group = 2
	shape.sensor = True
    	space.add(shape)
        return shape

    def get_kicker_points(self):
	p = self.robot.get_points()
        K = self.sim.scale * World.KickerReach
        sine, cosine = \
            K*cos(self.robot.body.angle), \
            K*sin(self.robot.body.angle)
    	bb = [ p[1] - self.robot.body.position,
               p[1] - self.robot.body.position + [sine, cosine],
               p[2] - self.robot.body.position +[sine, cosine],
               p[2] - self.robot.body.position]
	return bb

    def draw(self):
        self.draw_outline()
        self.draw_kickzone()
        self.draw_wheel(self.wheel_left)
        self.draw_wheel(self.wheel_right)

    def draw_outline(self):
    	ps = self.robot.get_points()
    	ps.append(ps[0])
        pygame.gfxdraw.filled_polygon(self.sim.screen, ps, THECOLORS['blue'])
	#pygame.draw.lines(self.sim.screen, THECOLORS["blue"], False, ps, 4)

    def draw_kickzone(self):
        #return
    	#ps = self.get_kicker_points()
	#pygame.draw.lines(self.sim.screen, THECOLORS["red"], False, ps, 3)
	ps = self.kickzone.get_points()
	pygame.draw.lines(self.sim.screen, THECOLORS["red"], False, ps, 3)

    def draw_wheel(self, wheel):
        ps = wheel.get_points()
        ps.append(ps[0])
        pygame.gfxdraw.filled_polygon(self.sim.screen, ps, THECOLORS['black'])
        #pygame.draw.lines(self.sim.screen, THECOLORS["black"], False, ps, 5)

        #Draw wheel direction markers
        pos = map(int, wheel.body.position + [5*cos(wheel.body.angle),
                                              5*sin(wheel.body.angle)])
        pygame.draw.circle(self.sim.screen, THECOLORS['yellow'], pos, 2)

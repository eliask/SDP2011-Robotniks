import sys
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
from math import *

def main():
	pygame.init()
	screen = pygame.display.set_mode((769, 424))
	clock = pygame.time.Clock()
	running = True

	### Physics stuff
	pymunk.init_pymunk()
	space = pymunk.Space()
	space.gravity = (0,0)
	space.damping = 0.6

	### Adding the object to the space
	walls = add_walls(space)
	ball = add_ball(space)
	us = add_robot(space)
	wheel1 = add_wheel_front(space, us)
	wheel2 = add_wheel_back(space, us)
	us.body.position = (100,100)
	wheel1.body.position = (100, 100)
	wheel2.body.position = (100, 100)
	robot_img = pygame.image.load("yellow_robot.png")
	speed = (0,0)
	
	while running:
		for event in pygame.event.get():
			if event.type == QUIT:
				running = False
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				running = False
			elif event.type == KEYDOWN and event.key == K_w:
				speed = (100*cos(us.body.angle), 100*sin(us.body.angle))
			elif event.type == KEYDOWN and event.key == K_s:
				speed = (0,0)
			elif event.type == KEYDOWN and event.key == K_a:
				us.body.angle -= radians(5)
			elif event.type == KEYDOWN and event.key == K_d:
				us.body.angle += radians(5)
			elif event.type == KEYDOWN and event.key == K_r:
				us.body.angle = 0 
			elif event.type == KEYDOWN and event.key == K_SPACE:
				ball.body.apply_impulse((100*cos(us.body.angle), 100*sin(us.body.angle)), (0,0))
			elif event.type == KEYDOWN and event.key == K_t:
				wheel1.body.velocity = (100, 0)
				wheel2.body.velocity = (100, 0)


		screen.fill(THECOLORS["green"])
				
		draw_walls(screen, walls)		
		draw_ball(screen, ball)
		draw_robot(screen, us, robot_img)
		draw_wheel(screen, wheel1)
		draw_wheel(screen, wheel2)
		#us.body.velocity = speed
		
		#kickZone = pymunk.Poly(us.body, kick_bounding_box(screen, us))
		kick_bounding_box(screen, us)
		space.step(1/50.0)

		pygame.display.flip()
		clock.tick(50)
		pygame.display.set_caption("fps: " + str(clock.get_fps()))	
			

def add_walls(space):
        static_body = pymunk.Body(pymunk.inf, pymunk.inf)
        static_lines = [pymunk.Segment(static_body, (10.0, 10.0), (10.0, 112.0), 1.0)
                                ,pymunk.Segment(static_body, (10.0, 112.0), (1.0, 112.0), 1.0)
                                ,pymunk.Segment(static_body, (1.0, 112.0), (1.0, 312.0), 1.0)
                                ,pymunk.Segment(static_body, (1.0, 312.0), (10.0, 312.0), 1.0)
                                ,pymunk.Segment(static_body, (10.0, 312.0), (10.0, 414.0), 1.0)
                                ,pymunk.Segment(static_body, (10.0, 414.0), (758.0, 414.0), 1.0)
                                ,pymunk.Segment(static_body, (758.0, 414.0), (758.0, 312.0), 1.0)
                                ,pymunk.Segment(static_body, (758.0, 312.0), (767.0, 312.0), 1.0)
                                ,pymunk.Segment(static_body, (767.0, 312.0), (767.0, 112.0), 1.0)
                                ,pymunk.Segment(static_body, (767.0, 112.0), (758.0, 112.0), 1.0)
                                ,pymunk.Segment(static_body, (758.0, 112.0), (758.0, 10.0), 1.0)
                                ,pymunk.Segment(static_body, (758.0, 10.0), (10.0, 10.0), 1.0)]

        for line in static_lines:
                line.elasticity = 0.3 
                line.group = 1
        space.add_static(static_lines)
	return static_lines

def draw_walls(screen, walls):
	for line in walls:
                        body = line.body
                        pv1 = body.position + line.a.rotated(body.angle)
                        pv2 = body.position + line.b.rotated(body.angle)
                        pygame.draw.lines(screen, THECOLORS["black"], False, [pv1,pv2])

def add_ball(space):
	mass = 1
	radius = 5
	inertia = pymunk.moment_for_circle(mass, 0, radius)
	body = pymunk.Body(mass, inertia)
	body.position = 384,210 
	shape = pymunk.Circle(body, radius)
	shape.elasticity = 0.7
	shape.friction = 0.9
	space.add(body, shape)
	return shape


def draw_ball(screen, ball):
	p = int(ball.body.position.x), int(ball.body.position.y)
	pygame.draw.circle(screen, THECOLORS["red"], p, int(ball.radius), 5)

def add_robot(space):
	fp = [(-30, -20), (30, -20), (30, 20), (-30, 20)]
	mass = 	1000
	moment = pymunk.moment_for_poly(mass, fp)
	robot_body = pymunk.Body(mass, moment)

	robot_shape = pymunk.Poly(robot_body, fp)
	robot_shape.friction = 0.99
	robot_shape.group = 2
	space.add(robot_body, robot_shape)
	
	return robot_shape	

def draw_robot(screen, robot, robot_img):
	p = robot.body.position
	rotated_robot_img = pygame.transform.rotate(robot_img, -degrees(robot.body.angle))

	offset = [rotated_robot_img.get_size()[0]/2, rotated_robot_img.get_size()[1]/2] 
	p = p - offset
	#screen.blit(rotated_robot_img, p)
	
	### draw lines around the robot
	ps = robot.get_points()
	ps.append(ps[0])
	pygame.draw.lines(screen, THECOLORS["blue"], False, ps)
	
def add_wheel_front(space, robot):
	w1 = [ (20,-15), (25,-15) ]

	moment_wheel_front = pymunk.moment_for_segment(1000, (20,-15), (25,-15))
	wheel_front_body= pymunk.Body(1000, moment_wheel_front)
	wheel_front_shape = pymunk.Segment(wheel_front_body, (20,-15), (25,-15), 1.0)
	wheel_front_shape.group = 2
	rotation_wheel_front = pymunk.PinJoint(robot.body, wheel_front_body, (22.5, -15), (22.5, -15))
		
	space.add(wheel_front_body, wheel_front_shape, rotation_wheel_front)
	return wheel_front_shape 

def add_wheel_back(space, robot):
	w1 = [ (-20,15), (-25,15) ]

	moment_wheel_front = pymunk.moment_for_segment(1000, (-20,15), (-25,15))
	wheel_front_body= pymunk.Body(1000, moment_wheel_front)
	wheel_front_shape = pymunk.Segment(wheel_front_body, (-20,15), (-25,15), 1.0)
	wheel_front_shape.group = 2
	rotation_wheel_front = pymunk.PinJoint(robot.body, wheel_front_body, (-22.5, 15), (-22.5, 15))
		
	space.add(wheel_front_body, wheel_front_shape, rotation_wheel_front)
	return wheel_front_shape 

def draw_wheel(screen, wheel):
	body = wheel.body
	pv1 = body.position + wheel.a.rotated(body.angle)
	pv2 = body.position + wheel.b.rotated(body.angle)
	pygame.draw.lines(screen, THECOLORS["red"], False, [pv1, pv2])
	

def kick_bounding_box(screen, robot):
	p = robot.get_points()
	bb = []
	bb.append((p[1][0], p[1][1]) )
	bb.append((p[1][0]+6*cos(robot.body.angle), p[1][1]+6*sin(robot.body.angle)) )
	bb.append((p[2][0]+6*cos(robot.body.angle), p[2][1]+6*sin(robot.body.angle)) )
	bb.append((p[2][0], p[2][1]) )

	pygame.draw.lines(screen, THECOLORS["red"], False, bb)	
	return bb


if __name__ == '__main__':
	sys.exit(main())

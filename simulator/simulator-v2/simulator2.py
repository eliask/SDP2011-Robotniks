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
	#space.damping = 0.6

	### Adding the object to the space
	walls = add_walls(space)
	ball = add_ball(space)

	### Initialisation of the robot
	us = add_robot(space)
	kickZone = kick_bounding_box(space, us)
	wheel1 = add_wheel_right(space, us)
	wheel2 = add_wheel_left(space, us)
	us.body.position = (100,100)
	wheel1.body.position = (115, 85)
	wheel2.body.position = (85, 115)
	cons1 = pymunk.SimpleMotor(us.body, wheel1.body, 0)
	cons2 = pymunk.SimpleMotor(us.body, wheel2.body, 0)
	space.add(cons1, cons2)

	### Loading sprites
	robot_img = pygame.image.load("yellow_robot.png")
	pitch_img = pygame.image.load("calibrated-background-cropped.png")
	ball_img = pygame.image.load("ball.png")


	while running:
		for event in pygame.event.get():
			if event.type == QUIT:
				running = False
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				running = False
			elif event.type == KEYDOWN and event.key == K_s:
				stop(us, wheel1, wheel2)
			elif event.type == KEYDOWN and event.key == K_a:
				wheel1.body.angle -= radians(5)
				wheel2.body.angle -= radians(5)
			elif event.type == KEYDOWN and event.key == K_d:
				wheel1.body.angle += radians(5)
				wheel2.body.angle += radians(5)
			elif event.type == KEYDOWN and event.key == K_r:
				reset(us, wheel1, wheel2)
			elif event.type == KEYDOWN and event.key == K_SPACE:
				kick(us, ball, kickZone)
			elif event.type == KEYDOWN and event.key == K_w:
				drive(wheel1, wheel2)
			elif event.type == KEYDOWN and event.key == K_c:
				startSpinRight(us, wheel1, wheel2)
			elif event.type == KEYDOWN and event.key == K_z:
				startSpinLeft(us, wheel1, wheel2)
			elif event.type == KEYDOWN and event.key == K_x:
				stopSpin(us, wheel1, wheel2)


		#screen.fill(THECOLORS["green"])
		screen.blit(pitch_img, (0,0))

		#draw_walls(screen, walls)
		draw_ball(screen, ball, ball_img)
		draw_robot(screen, us, robot_img)
		draw_wheel(screen, wheel1)
		draw_wheel(screen, wheel2)
		#draw_kick_zone(screen, kickZone)


		ball.body.velocity.x = ball.body.velocity.x / 1.007
		ball.body.velocity.y = ball.body.velocity.y / 1.007
		#print ball.body.velocity

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
	body.position = 384,212
	shape = pymunk.Circle(body, radius)
	shape.elasticity = 0.1
	shape.friction = 0.9
	shape.group = 3
	space.add(body, shape)
	return shape


def draw_ball(screen, ball, img):
	p = int(ball.body.position.x), int(ball.body.position.y)
	#pygame.draw.circle(screen, THECOLORS["red"], p, int(ball.radius), 5)
	screen.blit(img, p)

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
	screen.blit(rotated_robot_img, p)

	### draw lines around the robot
	ps = robot.get_points()
	ps.append(ps[0])
	#pygame.draw.lines(screen, THECOLORS["blue"], False, ps)

def add_wheel(space, robot, pos):
        scale = 15 # Wheel distance from body center
        fp = [(-3, -1), (3, -1), (3, 1), (-3, 1)]
        mass = 1000
        moment = pymunk.moment_for_poly(mass, fp)
        wheel_body = pymunk.Body(mass, moment)
        wheel_shape = pymunk.Poly(wheel_body, fp)
        wheel_shape.group = 2
	wheel_body.position = (robot.body.position[0] + scale*pos[0],
                               robot.body.position[1] + scale*pos[1])
	joint = pymunk.PivotJoint(robot.body, wheel_body, wheel_body.position)
        space.add(wheel_body, wheel_shape, joint)
        return wheel_shape

def add_wheel_right(space, robot):
        return add_wheel(space, robot, (1, -1))

def add_wheel_left(space, robot):
        return add_wheel(space, robot, (-1, 1))

def draw_wheel(screen, wheel):
        ps = wheel.get_points()
        ps.append(ps[0])
        pygame.draw.lines(screen, THECOLORS["black"], False, ps)

def kick_bounding_box(space, robot):
	p = robot.get_points()
	bb = []
	bb.append((p[1][0], p[1][1]) )
	bb.append((p[1][0]+10*cos(robot.body.angle), p[1][1]+10*sin(robot.body.angle)) )
	bb.append((p[2][0]+10*cos(robot.body.angle), p[2][1]+10*sin(robot.body.angle)) )
	bb.append((p[2][0], p[2][1]) )
	shape = pymunk.Poly(robot.body, bb)
	shape.group = 3
	space.add(shape)
	return shape

def draw_kick_zone(screen, zone):
	ps = zone.get_points()
	pygame.draw.lines(screen, THECOLORS["red"], False, ps)


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

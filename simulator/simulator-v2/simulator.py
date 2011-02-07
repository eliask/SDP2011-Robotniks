import pygame
from pygame.locals import *
from pygame.color import *
import pymunk as pm
from pymunk import Vec2d
import math, sys, random

pygame.init()
screen = pygame.display.set_mode((1024, 600))
clock = pygame.time.Clock()
running = True

### Physics stuff
pm.init_pymunk()
space = pm.Space()
space.resize_static_hash()
space.resize_active_hash()


### walls
static_body = pm.Body(pm.inf, pm.inf)
static_lines = [pm.Segment(static_body, (0, 0), (0, 565), 0),
		pm.Segment(static_body, (0, 565), (1024, 565), 0),
		pm.Segment(static_body, (1024, 565), (1024, 0), 0),
		pm.Segment(static_body, (1024, 0), (0, 0), 0)]
for line in static_lines:
    line.elasticity = 0.95
space.add_static(static_lines)

balls = []

def to_pygame(p):
    return int(p.x), int(-p.y+600)

# Add Ball
def add_ball(velocity):
	mass = 10
        radius = 25
        inertia = pm.moment_for_circle(mass, 0, radius, (0,0))
        body = pm.Body(mass, inertia)
        x = random.randint(0, 1024)
        body.position = x, 300
	body.apply_impulse((10, 20))
	body.velocity = velocity
        shape = pm.Circle(body, radius, (0,0))
        shape.elasticity = 0.95
	shape.friction = 100.0
        space.add(body, shape)
        balls.append(shape)

velocity = 500
add_ball((-velocity, 200))
add_ball((velocity, 300))
friction = 2
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
    screen.blit(pygame.image.load('bg.png'), (0,0))
    for ball in balls:
	p = to_pygame(ball.body.position)
        pygame.draw.circle(screen, THECOLORS["blue"], p, int(ball.radius), 2)

    for line in static_lines:
        body = line.body
        
    ### Update physics
    dt = 1.0/60.0
    for x in range(1):
        space.step(dt)
    
    ### Flip screen
    pygame.display.flip()
    clock.tick(50)
    pygame.display.set_caption("[SDP9 Simulator] fps: " + str(int(clock.get_fps())))
        

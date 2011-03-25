from pygame.locals import *
from math import *
import logging
import numpy as np
import pygame, pymunk

class Input:

    def __init__(self, sim):
        self.sim = sim
        self.initKeymap(sim.robots[0])
        self.command_string = ''
        self.place_object_num = 0
        self.button_down = False

    def initKeymap(self, robot):
        self.keymap = {
            # "reversed" controls for intuitiveness
            K_r : ( lambda:robot.drive_left(3),   lambda:robot.drive_left(0) ),
            K_w : ( lambda:robot.drive_right(3),  lambda:robot.drive_right(0) ),
            K_f : ( lambda:robot.drive_left(-3),  lambda:robot.drive_left(0) ),
            K_s : ( lambda:robot.drive_right(-3), lambda:robot.drive_right(0) ),

            K_a : ( lambda:robot.steer_left_incr(90), None ),
            K_q : ( lambda:robot.steer_left_incr(-90), None ),
            K_d : ( lambda:robot.steer_right_incr(90), None ),
            K_e : ( lambda:robot.steer_right_incr(-90), None ),
            K_SPACE : ( robot.kick,   None ),
            K_RETURN : ( self.command,   None ),

	    K_0 : ( self.sim.reset, None ),
	    K_p : ( self.sim.pause, None ),

            K_1 : ( lambda:self.initKeymap(self.sim.robots[0]), None ),
            K_2 : ( lambda:self.initKeymap(self.sim.robots[1]), None ),

            K_5 : ( self.sim.penalty_left,  None ),
            K_6 : ( self.sim.penalty_right, None ),
            }

    def robotInput(self, event):
        try:
            if event.type == KEYDOWN:
                start, _ = self.keymap.get(event.key, (None, None))
                if start: start()
            elif event.type == KEYUP:
                _, stop = self.keymap.get(event.key, (None, None))
                if stop: stop()
            elif event.type == MOUSEBUTTONDOWN:
                self.mouseInput(event)

        except (IndexError, KeyError, AttributeError):
            raise

        if event.type == KEYDOWN:
            self.commandInput(event)

        if self.button_down:
            self.sim.ball.body.position = pymunk.Vec2d(pygame.mouse.get_pos())
            self.sim.ball.body.velocity = pymunk.Vec2d((0,0))
            self.sim.ball.body.angular_velocity = 0

    def mouseInput(self, event):
        pos = event.pos
        if event.button == 1:
            self.button_down = True
        elif event.button == 3:
            self.button_down = False

    def command(self):
        N = int( self.command_string[0] )
        num = float( self.command_string[1:] )
        self.command_string = ''

        print "Command id:%d val:%d" % (N, num)
        self.sim.speed = int(num)

        return
        angle = radians(int( self.command_string[1:] ))
        if N == 1:
            self.p1.setRobotDirection(angle)
        elif N == 2:
            self.p2.setRobotDirection(angle)

    def commandInput(self, event):
        try:
            char = chr(event.key)
        except ValueError:
            return

        if '0' <= char <= '9' or char == '.':
            self.command_string += char

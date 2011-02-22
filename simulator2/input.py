from pygame.locals import *
from math import *
import logging
import numpy as np
import pygame

class Input:

    def __init__(self, sim, p1, p2):
        self.sim = sim
        self.p1 = p1
        self.p2 = p2
        self.initKeymap(p1, p2)
        self.command_string = ''
        self.place_object_num = 0
        self.button_down = False

    def initKeymap(self, p1, p2):
        self.keymap = {
            # "reversed" controls for intuitiveness
            K_r : ( lambda:p1.drive_left(3),   lambda:p1.drive_left(0) ),
            K_w : ( lambda:p1.drive_right(3),  lambda:p1.drive_right(0) ),
            K_f : ( lambda:p1.drive_left(-3),   lambda:p1.drive_left(0) ),
            K_s : ( lambda:p1.drive_right(-3),  lambda:p1.drive_right(0) ),

            K_a : ( lambda:p1.steer_left_incr(45), None ),
            K_q : ( lambda:p1.steer_left_incr(-45), None ),
            K_d : ( lambda:p1.steer_right_incr(45), None ),
            K_e : ( lambda:p1.steer_right_incr(-45), None ),
            K_SPACE : ( p1.kick,   None ),
            K_RETURN : ( self.command,   None ),
	    #K_x : ( p1.reset, None ),
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

        return
        if self.button_down:
            self.sim.world.ents['ball'].pos = pygame.mouse.get_pos()
            self.sim.world.ents['ball'].velocity = np.array([0,0])

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
        from strategy import apf
        if N == 1:
            apf.scaleT1 = num
            #self.sim.apf_scale = num
        elif N == 2:
            apf.scaleT2 = num
            #self.sim.apf_dist = num
        elif N == 3:
            apf.scaleA = num
        elif N == 4:
            apf.offset = num

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

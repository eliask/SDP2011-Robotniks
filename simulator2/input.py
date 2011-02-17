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
            K_w : ( p1.drive,  p1.stop ),
            #K_s : ( p1.driveR, p1.stop ),
            K_a : ( p1.startSpinLeft,   p1.stopSpin ),
            K_d : ( p1.startSpinRight,  p1.stopSpin ),
            K_c : ( p1.spinRightShort, None ),
            K_z : ( p1.spinLeftShort, None ),
            K_d : ( p1.startSpinRight,  p1.stopSpin ),
            K_x : ( p1.stopSpin, None ),
            K_e : ( p1.kick,   None ),
	    K_r : ( p1.reset, None ),

            K_u : ( p2.drive,  p2.stop ),
            #K_j : ( p2.driveR, p2.stop ),
            K_h : ( p2.startSpinLeft,   p2.stopSpin ),
            K_l : ( p2.startSpinRight,  p2.stopSpin ),
            K_m : ( p2.startSpinLeft, None ),
            K_n : ( p2.stopSpin, None ),
            K_y : ( p2.kick,   None ),
            }

    def robotInput(self, event):
        try:
            if event.type == KEYDOWN:
                start, _ = self.keymap.get(event.key, (None, None))
                if start: start()
            elif event.type == KEYUP:
                _, stop = self.keymap.get(event.key, (None, None))
                if stop: stop()
            elif event.type == KEYDOWN:
                self.commandInput(event)
            elif event.type == MOUSEBUTTONDOWN:
                self.mouseInput(event)

        except (IndexError, KeyError, AttributeError):
            raise

        if self.button_down:
            self.sim.world.ents['ball'].pos = pygame.mouse.get_pos()
            self.sim.world.ents['ball'].velocity = np.array([0,0])

    def mouseInput(self, event):
        pos = event.pos
        if event.button == 1:
            self.button_down = True
        elif event.button == 3:
            self.button_down = False

    def commandInput(self, event):
        try:
            char = chr(event.key)
        except ValueError:
            return

        if '0' <= char <= '9':
            if len(self.command_string) == 0 and char in "12":
                self.command_string += char

            if len(self.command_string) == 4:
                robot_num = int( self.command_string[0] )
                angle = radians(int( self.command_string[1:] ))
                if robot_num == 1:
                    self.p1.setRobotDirection(angle)
                elif robot_num == 2:
                    self.p2.setRobotDirection(angle)

                self.command_string = ''

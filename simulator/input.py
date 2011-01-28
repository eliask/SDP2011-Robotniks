from pygame.locals import *
from math import *
import logging

class Input:

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.initKeymap(p1, p2)
        self.command_string = ''

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
            start, stop = self.keymap.get(event.key, (None, None))
            if event.type == KEYDOWN and start:
                start()
            elif event.type == KEYUP and stop:
                stop()
            elif event.type == KEYDOWN:
                self.commandInput(event)

        except (IndexError, KeyError, AttributeError):
            pass

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

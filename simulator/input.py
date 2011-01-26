from pygame.locals import *

class Input:

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.initKeymap(p1, p2)

    def initKeymap(self, p1, p2):
        self.keymap = {
            K_w : ( p1.drive,  p1.stop ),
            K_s : ( p1.driveR, p1.stop ),
            K_a : ( p1.startSpinLeft,   p1.stopSpin ),
            K_d : ( p1.startSpinRight,  p1.stopSpin ),
            K_z : ( p1.startSpinLeft, lambda:None ),
            K_x : ( p1.stopSpin, lambda:None ),
            K_e : ( p1.kick,   lambda:None ),
	    K_r : ( p1.reset, lambda:None ),

            K_u : ( p2.drive,  p2.stop ),
            K_j : ( p2.driveR, p2.stop ),
            K_h : ( p2.startSpinLeft,   p2.stopSpin ),
            K_l : ( p2.startSpinRight,  p2.stopSpin ),
            K_m : ( p2.startSpinLeft, lambda:None ),
            K_n : ( p2.stopSpin, lambda:None ),
            K_y : ( p2.kick,   lambda:None ),
            }

    def robotInput(self, event):
        action = None
        if event.type == KEYDOWN:
            action = self.keymap.get(event.key, (None,None))[0]
        elif event.type == KEYUP:
            action = self.keymap.get(event.key, (None,None))[1]
        if action:
            action()

from pygame.locals import *

class Input:

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.initKeymap(p1, p2)

    def initKeymap(self, p1, p2):
        self.keymap = {
            K_w : ( p1.drive,  p1.stopDrive ),
            K_s : ( p1.driveR, p1.stopDrive ),
            K_a : ( p1.turn,   p1.stopTurn ),
            K_d : ( p1.turnR,  p1.stopTurn ),
            K_z : ( p1.startSpin, lambda:None ),
            K_x : ( p1.stopSpin, lambda:None ),
            K_e : ( p1.kick,   lambda:None ),
	    K_r : ( p1.reset, lambda:None ),

            K_u : ( p2.drive,  p2.stopDrive ),
            K_j : ( p2.driveR, p2.stopDrive ),
            K_h : ( p2.turn,   p2.stopTurn ),
            K_l : ( p2.turnR,  p2.stopTurn ),
            K_m : ( p2.startSpin, lambda:None ),
            K_n : ( p2.stopSpin, lambda:None ),
            K_y : ( p2.kick,   lambda:None ),
            }

        self.rawKeymap = {
            K_q : ( p1.rot1,   p1.stopRot1  ),
            K_a : ( p1.rot1R,  p1.stopRot1  ),
            K_r : ( p1.rot2,   p1.stopRot2  ),
            K_f : ( p1.rot2R,  p1.stopRot2  ),
            K_w : ( p1.move1,  p1.stopMove1 ),
            K_s : ( p1.move1R, p1.stopMove1 ),
            K_e : ( p1.move2,  p1.stopMove2 ),
            K_d : ( p1.move2R, p1.stopMove2 ),

            K_u : ( p2.rot1,   p2.stopRot1  ),
            K_h : ( p2.rot1R,  p2.stopRot1  ),
            K_p : ( p2.rot2,   p2.stopRot2  ),
            K_l : ( p2.rot2R,  p2.stopRot2  ),
            K_i : ( p2.move1,  p2.stopMove1 ),
            K_j : ( p2.move1R, p2.stopMove1 ),
            K_o : ( p2.move2,  p2.stopMove1 ),
            K_k : ( p2.move2R, p2.stopMove1 ),
            }

    def robotInput(self, event):
        action = None
        if event.type == KEYDOWN:
            action = self.keymap.get(event.key, (None,None))[0]
        elif event.type == KEYUP:
            action = self.keymap.get(event.key, (None,None))[1]
        if action:
            action()

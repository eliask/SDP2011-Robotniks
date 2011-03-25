from common.utils import *
from common.world import *
from communication.interface import *
from math import *
from main2 import *
import apf
import logging
import pygame

class PenaltyD(Main2):
    startX = 0
    timer = 0
    speed = 1
    
    def __init__(self, *args):
        Main2.__init__(self, *args, name='penaltydef')

    def run(self):
        if self.lock_until > time.time():
            return
        else:
            if self.post_lock(): return
            self.post_lock = lambda:None
        
        try:
            self.me = self.getSelf() # Find out where I am
        except Exception, e:
            logging.warn("couldn't find self: %s", e)
            return

        ball = self.world.getBall()
        if self.me.pos[0] == 0 or ball.pos[0] == 0:
            self.drive_both(0)
            print "Ball or self at 0: doing nothing"
            return
        
        Y = self.getMyGoalPos()[1]
        
        if self.startX == 0:
            self.startX = self.me.pos[0]
            return self.moveTo((self.startX, Y), speed=1)
        
        def foo():
            self.drive_both(self.speed)
            self.speed = - self.speed
        self.post_lock = foo
        self.lock_until = self.getTimeUntil(0.2)

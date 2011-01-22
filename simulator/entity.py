from pygame.locals import *
import pygame
import numpy as np

class Entity(pygame.sprite.Sprite):
    def __init__(self, sim, pos, image):
        pygame.sprite.Sprite.__init__(self)
        self.sim = sim
        self.pos = pos
        self.rect = image.get_rect()
        self.base_image = image
        self.image = image
        self.v = np.array([0.0, 0.0])
        self.move()

    def move(self):
        self.pos = ( self.pos[0] + self.v[0], self.pos[1] + self.v[1] )
        self.rect.center = self.pos

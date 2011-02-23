from pygame.locals import *
import pygame
import numpy as np

class Entity(pygame.sprite.Sprite):
    def __init__(self, sim, pos, image):
        pygame.sprite.Sprite.__init__(self)
        self.sim = sim
        self.pos = np.array(pos)
        self.rect = image.get_rect()
        self.base_image = image
        self.image = image
        self.v = np.array((0.0, 0.0))
        self.move()

    def move(self):
        self.pos += self.v
        self.rect.center = self.pos

        assert (self.pos >= 0).all(), "Entiy position must be positive"

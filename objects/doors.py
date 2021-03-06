import random

import fx
import pygame
from animations import *
from stgs import *
   
class door(pygame.sprite.Sprite):
    color = (255, 255, 255)

    def __init__(self, game, objT, **kwargs):
        self.groups = game.sprites, game.layer1
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.lID = objT.id
        self.rect = pygame.Rect(objT.x, objT.y, objT.width, objT.height)
        self.game = game
        self.game.level.door = self
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.parts = fx.particles(self.game, pygame.Rect(self.rect.x, self.rect.y, 64, 12), tickSpeed=2, size = 14)
        self.parts.setParticleKwargs(speed=1.5, shrink=0.4, life=140, color=colors.orangeRed)

    def kill(self):
        self.parts.kill()
        super().kill()

class entrance(pygame.sprite.Sprite):
    color = (255, 255, 255)

    def __init__(self, game, objT, **kwargs):
        self.groups = game.sprites, game.layer1
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.lID = objT.id
        game.level.entrance = self
        self.rect = pygame.Rect(objT.x, objT.y, objT.width, objT.height)

        for k, v in kwargs.items():
            self.__dict__[k] = v

        #self.image = pygame.Surface((self.rect.width, self.rect.height))
        #self.image.fill(self.color)

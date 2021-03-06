import pygame
from stgs import *

class cam:

    def __init__(self, game, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.limit = CAMLIMIT
        self.game = game
        self.target = game.player

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def applyRect(self, rect):
        return rect.move(self.camera.topleft)

    def toggleTarget(self):
        if self.target == self.game.player:
            self.target = self.game.level.door
        else:
            self.target = self.game.player
        
    def update(self):

        x = -self.target.rect.centerx + int(winWidth / 2)
        y = -self.target.rect.centery + int(winHeight / 2)

        # limit scrolling to map size
        if self.limit:
            x = min(0, x)  # left
            y = min(0, y)  # top
            x = max(-(self.width - winWidth), x)  # right
            y = max(-(self.height - winHeight), y)  # bottom

        self.camera = pygame.Rect(x, y, self.width, self.height)
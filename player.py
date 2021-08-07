#### Imports ####

import math

import pygame

from animations import *
from objects import *
from stgs import *
import fx


#### Player object ####
class player(pygame.sprite.Sprite):
    x = 71
    y = 71
    yModMin = -0.12
    yModMax = 0.25
    hitCooldown = 500
    lastHit = 0
    roomBound = True
    imgSheet = {'active': False, 'tileWidth': 64, 'r': False, 'l': False, 'idleR': False, 'flyR': False, 'flyL': False}
    width, height = 28, 24
    health = 50
    maxHp = 50
    attempts = 0
    #### Player Initializations ####
    def __init__(self, game, image, name, **kwargs):
        self.groups = [game.sprites, game.layer2]
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        self.image = pygame.image.load(image)
        self.imgSrc = self.image.copy()
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.moveRect = pygame.Rect(self.rect)
        self.dir = pygame.math.Vector2((0, 0))
        self.vel = 20
        self.spinSpeed = 6
        self.drag = 0.99
        self.ground = False
        self.damage = 10
        self.canFire = False
        self.spinning = False
        self.fires = 0
        self.loop = 0
        self.lastFire = pygame.time.get_ticks()
        self.lastRebound = 0
        self.mask = pygame.mask.from_surface(self.image, True)
        self.angle = 0
        self.particleFx = fx.particles(self.game, self, size = 15,)
        self.particleFx.setParticleKwargs(color=colors.yellow, speed=5, shrink=0.6)

        for k, v in kwargs.items():
            self.__dict__[k] = v
        
        self.loadAnimations()

    def loadAnimations(self):
        pass
        #self.animations = animation(self)
        #self.animations.scale(2, 3)
        #self.animations.rotation = True

    #### Updates player ####
    def update(self):
        self.loop += 1
        if self.loop == 1:
            self.lastFire = pygame.time.get_ticks()
        if self.canFire:
            self.fire()
        if self.spinning:
            self.spin()

        if pygame.time.get_ticks() - self.lastFire >= 240 and self.fires == 0:
            self.canFire = True

        self.move()
        self.rotCenter()
        self.particleFx.entityRect = self.rect
        #self.animations.update()
    
    def takeDamage(self, damage):
        if pygame.time.get_ticks() - self.lastHit >= self.hitCooldown:
            self.health -= damage
            self.lastHit = pygame.time.get_ticks()
            self.game.mixer.playFx('pHit')
    
    def fire(self):
        if pygame.mouse.get_pressed()[0]: ## Checks on click 
            mPos = pygame.Vector2(pygame.mouse.get_pos())  ## Gets mouse position and stores it in vector. This will be translated into the vector that moves the bullet
            pPos = self.game.cam.apply(self)  ## Gets actual position of player on screen
            mPos.x -= pPos.centerx ## Finds the x and y relativity between the mouse and player and then calculates the offset
            mPos.y -= pPos.centery
            # print(mPos.normalize())
            try:
                self.angle = math.degrees(math.atan2(-mPos.normalize().y, mPos.normalize().x))
            except ValueError:
                self.angle = 0

            self.dir = mPos.normalize()*self.vel
            self.lastFire = pygame.time.get_ticks()
            self.lastRebound = pygame.time.get_ticks()
            #self.game.mixer.playFx('gunFx1')
            self.canFire = False
            self.spinning = False
            self.fires += 1
            self.game.startTime = True
            self.game.mixer.playFx('swing')
    
    def rotCenter(self, angle=False):
        if not angle:
            angle = self.angle
        self.image = pygame.transform.rotate(self.imgSrc, angle)
        self.rect = self.image.get_rect(center = self.image.get_rect(center = self.rect.center).center)
        self.mask = pygame.mask.from_surface(self.image, True)
    
    def spin(self):
        self.angle += self.spinSpeed

    #### Move Physics ####
    def move(self):
        self.moveRect.x += math.ceil(self.dir.x)
        collide = self.collideCheck()
        if collide:
            if self.dir.x > 0:
                self.moveRect.right = collide.left
            else: 
                self.moveRect.left = collide.right
            self.dir.x = 0
            self.dir.y = 0
        
        self.moveRect.y += math.ceil(self.dir.y)
        collide = self.collideCheck()
        if collide:
            if self.dir.y > 0:
                self.moveRect.bottom = collide.top
            else: 
                self.moveRect.top = collide.bottom
            self.dir.x = 0
            self.dir.y = 0

        self.rect.center = self.moveRect.center
        self.dir = self.dir*self.drag

        # if self.roomBound:
        #     self.moveRect.x = max(0, self.moveRect.x)
        #     self.moveRect.x = min(winWidth-self.moveRect.width, self.moveRect.x)
        #     self.moveRect.y = max(0, self.moveRect.y)
        #     self.moveRect.y = min(winHeight-self.moveRect.height, self.moveRect.y)

    #### Collide checker for player ####
    def collideCheck(self):
        returnVal = False
        testRect = self.moveRect#pygame.Rect(self.moveRect.x, self.moveRect.y)
        
        for obj in self.game.colliders:
            if isinstance(obj, rebound):
                if pygame.time.get_ticks() - self.lastRebound >= 200:
                    r2 = obj.rect
                    if self.mask.overlap(pygame.mask.Mask(r2.size, True), (r2.x-self.rect.x,r2.y-self.rect.y)):
                        self.dir = pygame.Vector2(0, 0)
                        self.canFire = True
                        self.spinning = True

            elif testRect.colliderect(obj.rect):
                returnVal = obj.rect  
            
        return returnVal
    
    def reset(self):
        self.game.startTime = False
        self.angle = 0
        self.fires = 0
        self.loop = 0
        self.dir = pygame.Vector2(0, 0)

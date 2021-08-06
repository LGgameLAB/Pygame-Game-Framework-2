import pygame
from stgs import *
from animations import *
import fx
import math

def activatePlatform(game, platformId):
    game.getSprBylID(platformId).pause = False

class trigger(pygame.sprite.Sprite):
    def __init__(self, game, rect, func, params, **kwargs):
        self.groups = game.sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pygame.Rect(rect)
        self.func = lambda:func(params[0], params[1])
        self.touched = False
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def update(self):
        if not self.touched:
            if self.rect.colliderect(self.game.player.rect):
                self.func()
                self.touched = True


class wall(pygame.sprite.Sprite):
    color = (255, 255, 255)

    def __init__(self, game, objT, **kwargs):
        self.groups = game.colliders
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.rect = pygame.Rect(objT.x, objT.y, objT.width, objT.height)

        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill(self.color)

class platWall(pygame.sprite.Sprite):
    color = (255, 255, 255)

    def __init__(self, game, objT, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(objT.x, objT.y, objT.width, objT.height)
        self.objT = objT
        
        for k, v in kwargs.items():
            self.__dict__[k] = v
        for k, v in objT.properties.items():
            self.__dict__[k] = v
            
        self.image = pygame.Surface((self.rect.width, self.rect.height))

class mPlatform(pygame.sprite.Sprite):
    def __init__(self, game, objT, **kwargs):
        self.groups = game.colliders, game.sprites, game.layer2
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pygame.Rect(objT.x, objT.y, objT.width, objT.height)
        self.pos = pygame.Vector2((self.rect.x, self.rect.y))
        self.player = self.game.player
        self.pause = False
        self.vertical = False
        self.dir = (1, 0)
        self.vel = 5
        self.color = (255, 255, 255)
        for k, v in kwargs.items():
            self.__dict__[k] = v
        for k, v in objT.properties.items():
            self.__dict__[k] = v

        if self.vertical:
            self.dir = (0, 1)

        self.dir = pygame.Vector2(self.dir).normalize()

        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.render()
    
    def render(self):
        defaultTile = Spritesheet(asset('../../CyberSpacePygame/assets/Tiled/tileset1.png')).get_image(0, 0, 32, 32)
        for x in range(0, self.image.get_width(), 32):
            self.image.blit(defaultTile, (x, 0))
    
    def update(self):
        if not self.pause:
            self.move()
            self.rect.x, self.rect.y = self.pos
    
    def move(self):
        testVec = pygame.Vector2((self.pos.x, self.pos.y))
        if self.collideCheck(pygame.Vector2(testVec.x+(self.dir.x*self.vel), testVec.y)):
            
            if self.dir.x > 0:
                self.dir = self.dir.reflect((-1,0))
            else:
                self.dir = self.dir.reflect((1,0))
        
        self.pos.x += self.dir.x*self.vel
        # If we hit player move the player
        testRect = pygame.Rect(self.pos.x, self.pos.y, self.rect.width, self.rect.height)
        if testRect.colliderect(self.player.rect):
            if self.dir.x < 0:
                self.player.rect.right = testRect.left
            else:
                self.player.rect.left = testRect.right

        if self.collideCheck(pygame.Vector2(testVec.x, testVec.y+(self.dir.y*self.vel))):
            if self.dir.y > 0:
                self.dir = self.dir.reflect((0, -1))
            else:
                self.dir = self.dir.reflect((0, 1))
        
        if self.dir.y > 0:
            moveP = self.checkPlayerAbove(testRect)
        else:
            moveP = False

        self.pos.y += self.dir.y*self.vel
        testRect = pygame.Rect(self.pos.x, self.pos.y, self.rect.width, self.rect.height)
        if moveP:
            self.player.rect.bottom = testRect.top
        
        testRect = pygame.Rect(self.pos.x, self.pos.y, self.rect.width, self.rect.height)
        if testRect.colliderect(self.player.rect):
            if self.dir.y < 0:
                self.player.rect.bottom = testRect.top
            else:
                self.player.rect.top = testRect.bottom

    def collideCheck(self, vector):
            returnVal = False
        
            testRect = pygame.Rect(round(vector.x), round(vector.y), self.rect.width, self.rect.height)
            for obj in self.game.colliders:
                if not obj == self:
                    if testRect.colliderect(obj.rect):
                        returnVal = True

            for obj in self.game.level.sprites:
                if isinstance(obj, platWall):
                    if testRect.colliderect(obj.rect):
                        returnVal = True
                    
            return returnVal

    def checkPlayerAbove(self, testRect):
        upRect = testRect.move(0, -1)
        if upRect.colliderect(self.player.rect):
            return True
        else:
            return False
    
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
  
class rebound(pygame.sprite.Sprite):
    color = (255, 255, 255)

    def __init__(self, game, objT, **kwargs):
        self.groups = game.sprites, game.layer1, game.colliders
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.lID = objT.id
        self.rect = pygame.Rect(objT.x, objT.y, objT.width, objT.height)
        self.game = game
        self.points = 10
        for k, v in kwargs.items():
            self.__dict__[k] = v
        for k, v in objT.properties.items():
            self.__dict__[k] = v

        self.parts = fx.particles(self.game, pygame.Rect(self.rect.x, self.rect.y, 64, 12), tickSpeed=2, size = 14)
        self.parts.setParticleKwargs(speed=1.5, shrink=0.4, life=140, color=colors.lightGreen)

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

class key(pygame.sprite.Sprite):
    color = (255, 255, 255)

    def __init__(self, game, objT, image, **kwargs):
        self.groups = game.sprites, game.layer1
        pygame.sprite.Sprite.__init__(self, self.groups)
        game.level.key = self

        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.image = pygame.image.load(image)
        self.pos = pygame.Vector2(objT.x, objT.y)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.image.get_width(), self.image.get_height())

class consumable(pygame.sprite.Sprite):
    imgSheet = {'active': False, 'static': True,'tileWidth': 32}
    image = pygame.Surface((imgSheet['tileWidth'], imgSheet['tileWidth']))

    def __init__(self, game, objT, **kwargs):
        self.game = game
        self.groups = game.sprites, game.items, game.layer1
        pygame.sprite.Sprite.__init__(self, self.groups)

        for k, v in kwargs.items():
            self.__dict__[k] = v

        if self.imgSheet['active']:
            self.animations = animation(self)

        self.pos = pygame.Vector2(objT.x, objT.y)
        self.rect = pygame.Rect(0, 0, self.imgSheet['tileWidth'], self.imgSheet['tileWidth'])
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

    def update(self):
        if self.imgSheet['active']:
            self.animations.update()
        
class dmgRect(pygame.sprite.Sprite):
    def __init__(self, game, rect, **kwargs):
        self.groups = game.dmgRects
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.damage = 5
        self.rect = pygame.Rect(rect)
        for k, v in kwargs.items():
            self.__dict__[k] = v

#### Bullet Class #### 
class bullet(pygame.sprite.Sprite):
    pos = pygame.Vector2((0,0))
    image = pygame.image.load(asset('objects/bullet2.png'))
    vel = 20
    offset = 0
    static = False
    def __init__(self, game, pos, target, angle, **kwargs):
        self.groups = game.sprites, game.pBullets, game.layer2
        self.game = game
        pygame.sprite.Sprite.__init__(self, self.groups)

        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.pos = pygame.Vector2(pos)
        self.dir = pygame.Vector2(target).normalize()
        self.dir = self.dir.rotate(self.offset)
        self.image = pygame.transform.rotate(self.image, angle - self.offset)
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.rect.center = self.pos
    
    def update(self):
        if not self.static:
            self.pos += self.dir *self.vel
            self.rect.center = self.pos

class healthBar(pygame.sprite.Sprite):
    x = winWidth/3
    y = 3
    width = 100
    height = 30
    bgColor = colors.light(colors.black, 50)
    hpColor = colors.lightGreen
    offset = 10
    gap = offset
    def __init__(self, game, player, **kwargs):
        self.groups = game.sprites, game.overlayer
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.player = player
        self.image = pygame.Surface((self.width, self.height))
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.barRect = pygame.Rect(self.offset/2, self.offset/2, self.width-self.gap, self.height-self.gap)
    
    def update(self):
        self.image.fill((self.bgColor))
        self.renderBar()
    
    def renderBar(self):
        pygame.draw.rect(self.image, self.hpColor, (self.barRect.x, self.barRect.y, (self.barRect.width)*(self.player.health/self.player.maxHp), self.barRect.height))
    # def renderBar(self):
    #     pygame.draw.rect(self.image, self.hpColor, (1, 1, (self.barRect.width)*(self.player.health/self.player.maxHp), self.barRect.height))

class healthBar2(healthBar):
    x = 5
    y = winHeight/3
    width = 30
    height = 100
    bgColor = colors.light(colors.black, 100)
    offset = 6
    gap = offset

    def __init__(self, game, player):
        super().__init__(game, player)
    def renderBar(self):
        pygame.draw.rect(self.image, self.hpColor, (self.barRect.x, self.barRect.y+(self.barRect.height)*(1 - self.player.health/self.player.maxHp), self.barRect.width, (self.barRect.height)*(self.player.health/self.player.maxHp)))

class coinMeter(pygame.sprite.Sprite):

    def __init__(self, game, player, **kwargs):
        self.groups = game.sprites, game.overlayer
        pygame.sprite.Sprite.__init__(self, self.groups)

        ## Setup
        self.x = 0
        self.y = 40
        self.width = 30
        self.height = 100
        self.bgColor = colors.rgba(colors.light(colors.black, 20), 120)
        self.coinColor = colors.yellow
        self.offset = 5
        self.gap = self.offset*2
        
        self.meterLevel = 0
        self.coins = 0
        self.coinsPerLevel = 5
        self.healthAddPerc = 0.2
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.player = player
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.barRect = pygame.Rect(self.offset, self.offset, self.width-self.gap, self.height-self.gap)
        
    
    def update(self):
        self.image.fill((self.bgColor))
        self.renderBar()
    
    def renderBar(self):
        pygame.draw.rect(self.image, self.coinColor, (self.barRect.x, self.barRect.y+(self.barRect.height)*(1 - self.meterLevel/self.coinsPerLevel), self.barRect.width, (self.barRect.height)*(self.meterLevel/self.coinsPerLevel)))

    def addCoin(self):
        self.coins += 1
        self.meterLevel += 1
        if self.meterLevel >= self.coinsPerLevel:
            self.meterLevel = 0
            self.player.health += self.player.maxHp*self.healthAddPerc
            self.player.health = min(self.player.maxHp, self.player.health)

class coinBit(consumable):
    def __init__(self, game, objT):
        super().__init__(game, objT, image = pygame.image.load(asset('objects/bitCoin.png')), value = 5)

class key1(key):
    def __init__(self, game, objT):
        super().__init__(game, objT, asset('objects/decryptor.png'))

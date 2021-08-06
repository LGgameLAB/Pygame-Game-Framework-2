import pygame

pygame.init()
import os
import random
import sys

from camera import *
from fx import *
from levels import *
from menu import *
from objects import *
from overlay import *
from player import *
from sfx import *
from stgs import *
import menus

loadSave(saveFile)
from stgs import *


#### Game object ####
class game:

    #### Initialize game object ####
    #
    # Groups each sprite type to perform targetted tasks
    # All sprites go into the sprites group
    # Sets up window, font, gravity, and cam
    # Loads data for the game levels and the player

    def __init__(self):
        self.layer1 = pygame.sprite.Group()
        self.layer2 = pygame.sprite.Group()
        self.fxLayer = pygame.sprite.Group()
        self.overlayer = pygame.sprite.Group()
        self.rendLayers = [self.layer1, self.layer2]
        self.mixer = gameMixer()
        self.mixer.setMusicVolume(musicVolume) # between 0 and 1
        self.mixer.setFxVolume(fxVolume)
        self.antialiasing = aalias

        #pygame.display.set_icon(pygame.image.load(iconPath))
        self.win = pygame.display.set_mode((winWidth, winHeight))
        pygame.display.set_caption("A Sword's Conquest")
        pygame.display.set_icon(pygame.image.load(iconPath))
        self.font1 = pygame.font.Font(os.path.join('fonts', 'YuseiMagic-Regular.ttf'), 48)
        self.font2 = pygame.font.SysFont('Comic Sans MS', 23)
        self.menuFont = pygame.font.Font(os.path.join('fonts', 'YuseiMagic-Regular.ttf'), 15)
        self.gameOverFont = pygame.font.Font(os.path.join('fonts', 'YuseiMagic-Regular.ttf'), 60)
        self.victoryFont = pygame.font.Font(os.path.join('fonts', 'YuseiMagic-Regular.ttf'), 72)
        self.lastPause = pygame.time.get_ticks()
        self.lastReset = pygame.time.get_ticks()
        self.lastCamTog = pygame.time.get_ticks()
        self.noCont = False
        self.points = 0
        self.gravity = 1.6
        self.currentFps = 0
        self.showFps = SHOWFPS
        self.fullScreen = False
        self.clock = pygame.time.Clock()
        self.new()

    def new(self):
        self.won = False
        self.points = 0
        self.enemies = pygame.sprite.Group()
        self.sprites = pygame.sprite.Group()
        self.pSprites = pygame.sprite.Group()
        self.colliders = pygame.sprite.Group()
        self.dmgRects = pygame.sprite.Group()
        self.pBullets = pygame.sprite.Group()
        self.eBullets = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.levels = gameLevels
        self.player = player(self, asset('player/sw1.png'), 'Cyber Man', imgSheet = 
            {'active': True, ## Will become deprecated but is usefulin current development. Allows use of sample image.
            'tileWidth': 64, 
            'r': asset('player/sw1.png'), 
            })
            
        self.player.gravity = self.gravity
        self.end = False
        self.attempts = 0
        self.pause = False
        self.pauseScreen = pauseOverlay(self)
        self.time = 0
        self.startTime = False
        self.updateT = pygame.time.get_ticks()
        self.cam = cam(self, winWidth, winHeight)

    ####  Determines how the run will function ####
    def run(self):
        self.menuLoop()
        #self.mixer.playMusic(asset('sounds/track 1.wav'))
        self.mainLoop()
        self.mixer.stop()
        if self.won:
            self.victoryLoop()
        else:
            self.gameOver()

    #### Controls how the levels will load ####
    def loadLevel(self, levelNum, *args):  
        self.noCont = False 
        self.player.reset()
        try:
            for obj in self.level.sprites:
                obj.kill()
        except:
            pass
        self.level = self.levels[levelNum-1] 
        self.level.load(self)
        
        self.cam.width, self.cam.height = self.level.rect.width, self.level.rect.height
        
        try:
            self.player.moveRect.topleft = self.level.entrance.rect.center
        except:
            print("No player Pos")

        self.time = 0
        #self.player.gun.recenter()

    #### Main game loop ####
    def mainLoop(self):
        
        while not self.end:
            self.clock.tick(FPS)
            self.refresh()#asset('objects/shocking.jpg'))

            ##Updates Game
            self.runEvents()
            self.update()

    def update(self): 
        self.getFps()
        self.getPause()
        if self.pause:
            self.pSprites.update()
            self.pauseScreen.update()
        else:
            self.sprites.update()
            self.checkHits()
        now = pygame.time.get_ticks()
        if checkKey(keySet['retry']) and now - self.lastReset >= 500:
            self.cont()
            self.attempts += 1
            self.lastReset = now
        if self.startTime and now - self.updateT >= 500:
            self.time += 1
            self.updateT = now
        self.cam.update()
        
        self.render()

        
        pygame.display.update()

    def render(self):
        self.win.blit(self.level.image, self.cam.apply(self.level))

        for layer in self.rendLayers:
            for sprite in layer:
                try:
                    self.win.blit(sprite.image, self.cam.apply(sprite))
                except:
                    pass
        
        for fx in self.fxLayer:
            self.win.blit(fx.image, fx.rect)
        
        for sprite in self.overlayer:
            self.win.blit(sprite.image, sprite.rect)
        
        
        if self.showFps:
            fpsText = fonts['6'].render(str(self.currentFps), self.antialiasing, (255, 255, 255))
            self.win.blit(fpsText, (1100, 5))
        
        ## Overlay text
        self.win.blit(transparentRect((180, 35), 100), (290, 22))
        visPoints = fonts['6'].render("Score: " + str(self.points), self.antialiasing, (255, 255, 255))
        if self.level.points > 0:
            visLvlPoints = fonts['6'].render('  + ' + str(self.level.points), self.antialiasing, colors.yellow)
            w = visPoints.get_width()+visLvlPoints.get_width() + 20
            self.win.blit(transparentRect((w, 35), 100), (90, 22))
            self.win.blit(visLvlPoints, (90 + visPoints.get_width(), 20))
        else:
            w = visPoints.get_width() + 20
            self.win.blit(transparentRect((w, 35), 100), (90, 22))
        
        visTime = fonts['6'].render("Time: " + str(self.time), self.antialiasing, (255, 255, 255))
        self.win.blit(transparentRect((visTime.get_width() + 20, 35), 100), (480, 22))
        
        visAttempts = fonts['6'].render("Attempts: " + str(self.attempts), self.antialiasing, (255, 255, 255))
        self.win.blit(visAttempts, (300, 20))
        self.win.blit(visPoints, (100, 20))
        self.win.blit(visTime, (490, 20))

    def checkHits(self):
        
        for e in self.enemies:
            r2 = e.rect
            if self.player.mask.overlap(pygame.mask.Mask(r2.size, True), (r2.x-self.player.rect.x,r2.y-self.player.rect.y)):
                try:
                    e.takeDamage(self.player.damage)
                except:
                    e.health -= self.player.damage
                if e.health <= 0:
                    e.deathSound()
                    self.level.points += e.points
                    self.level.enemyCnt -= 1

        for e in self.eBullets:
            r2 = e.rect
            if self.player.mask.overlap(pygame.mask.Mask(r2.size, True), (r2.x-self.player.rect.x,r2.y-self.player.rect.y)):
                self.mixer.playFx('pHit')
                self.pause = True
                self.attempts += 1
                fadeOut(self, speed = 2.5, alpha = 40, color = colors.dark(colors.red, 60), startDelay = 540, noKill = True, onEnd = self.died)

        pygame.sprite.groupcollide(self.colliders, self.pBullets, False, True)
        pygame.sprite.groupcollide(self.colliders, self.eBullets, False, True)

        items = pygame.sprite.spritecollide(self.player, self.items, True)
        for item in items:
            if isinstance(item, coinBit):
                self.points += item.value
                self.player.coinMeter.addCoin()

            elif isinstance(item, hpPack1):
                self.player.health += item.value

        tpCols = pygame.sprite.spritecollide(self.player, self.level.teleporters, False)
        for tp in tpCols:
            fadeOut(self, speed = 20, alpha = 120, fadeBack = True)
            self.player.rect.topleft = tp.target
            self.player.gun.recenter()

        r2 = self.level.door.rect
        if self.level.enemyCnt == 0 and self.player.mask.overlap(pygame.mask.Mask(r2.size, True), (r2.x-self.player.rect.x,r2.y-self.player.rect.y)):
            self.noCont = True
            self.pause = True
            self.points += self.level.points
            self.points += 100 - self.time
            self.level.points = 0
            self.startTime = False
            self.mixer.playFx('menu3')
            fadeOut(self, speed = 5, alpha = 40, onEnd = lambda:self.nextLevel())

        if self.player.dir == (0, 0) and self.player.fires > 0 and not self.player.canFire:
            self.mixer.playFx('pHit')
            self.pause = True
            self.attempts += 1
            self.startTime = False
            fadeOut(self, speed = 2.5, alpha = 40, color = colors.dark(colors.red, 60), startDelay = 540, noKill = True, onEnd = self.died)

    def unPause(self):
        self.pause = False
        self.pauseScreen.deactivate()
        self.overlayer.remove(self.pauseScreen)

    def endgame(self):
        self.unPause()
        self.end = True

    def reset(self):
        for sprite in self.sprites:
            sprite.kill()
        for sprite in self.pSprites:
            sprite.kill()
        self.new()
        self.run()

    def cont(self):
        if not self.noCont:
            self.cam.target = self.player
            self.pause = False
            self.enemies.empty()
            self.loadLevel(self.getLvlNum())
            self.player.reset()
            self.fxLayer.empty()
            for s in self.pSprites:
                s.kill()
            for b in self.eBullets:
                b.kill()

    def died(self):
        button(self, (400, 400), groups = [self.pSprites, self.overlayer], text = "Continue", onClick=self.cont, instaKill = True, center = True, colors = (colors.orangeRed, colors.white))
        def end():
            self.end = True
        button(self, (400, 500), groups = [self.pSprites, self.overlayer], text = "Return to menu", onClick=end, instaKill = True, center = True, colors = (colors.orangeRed, colors.white))
    
    def getLvlNum(self, offSet=0):
        return self.levels.index(self.level) + 1 + offSet

    def nextLevel(self):
        self.cam.target = self.player
        if DEBUG:
            try:
                self.loadLevel(self.levels.index(self.level) + 2)
                fadeIn(self, speed = 20, onEnd = lambda:self.unPause())
            except IndexError:
                self.end = True
                self.won = True
        else:
            try:
                self.loadLevel(self.levels.index(self.level) + 2)
                fadeIn(self, onEnd = lambda:self.unPause())
            except:
                self.end = True
                self.won = True

    def quit(self):
        saveData(saveFile, self)
        pygame.quit()
        sys.exit()

    def runEvents(self):    
        ## Catch all events here
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                self.quit()
        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.fullScreen:
                        self.win = pygame.display.set_mode((winWidth, winHeight))
                        self.fullScreen = False
                        pygame.display.set_icon(pygame.image.load(iconPath))
                    else:
                        self.quit()
        self.getFullScreen()
        if pygame.time.get_ticks() - self.lastCamTog >= 400 and checkKey(keySet['toggleCam']):
            self.toggleCam()
            self.lastCamTog = pygame.time.get_ticks()

    def getFps(self):
        self.currentFps = self.clock.get_fps() 
        return self.currentFps
    
    def toggleCam(self):
        self.cam.toggleTarget()

    def toggleFps(self):
        if self.showFps:
            self.showFps = False
        else:
            self.showFps = True

    def toggleAalias(self):
        if self.antialiasing:
            self.antialiasing = False
        else:
            self.antialiasing = True
        
        self.pauseScreen.loadComponents()

    def getFullScreen(self):
        keys = pygame.key.get_pressed()
        if keys[keySet['fullScreen']]:
            if self.fullScreen:
                self.win = pygame.display.set_mode((winWidth, winHeight))
                self.fullScreen = False
            else:
                self.win = pygame.display.set_mode((winWidth, winHeight), pygame.FULLSCREEN)
                self.fullScreen = True
            pygame.display.set_icon(pygame.image.load(iconPath))
            #pygame.display.toggle_fullscreen()

    def getPause(self):
        if pygame.time.get_ticks() - self.lastPause >= 180:
            keys = pygame.key.get_pressed()
            if keys[keySet['pause']]:
                if self.pause:
                    self.unPause()
                else:
                    self.pause = True
                    self.overlayer.add(self.pauseScreen)
                    self.pauseScreen.activate()

                self.lastPause = pygame.time.get_ticks()

    def getSprBylID(self, lID):
        for sprite in self.sprites:
            try:
                if sprite.lID == lID:
                    return sprite
            except:
                pass
        return False

    #### First menu loop ####
    def menuLoop(self):
        menus.main(self)

    def victoryLoop(self):
        menuButton = button(self, (winWidth/2, winHeight/2), text="Back to Menu", center = True, colors = (colors.yellow, colors.white))
        buttons = pygame.sprite.Group(menuButton)
        self.mixer.playFx('yay')
        while True:
            pygame.time.delay(50)
            
            self.runEvents()
            self.refresh()

            buttons.update()
            for btn in buttons:
                self.win.blit(btn.image, btn.rect)

            if menuButton.clicked:
                self.reset()
                break
            
            text1 = self.victoryFont.render('Victory', self.antialiasing, colors.yellow, 20)
            text2 = fonts['1'].render("Score: " + str(self.points), self.antialiasing, (colors.yellow))
            
            self.win.blit(text2, (800, 70))
            self.win.blit(text1, (winWidth/2 - text1.get_width()/2 ,30))
            
            pygame.display.update()

    def gameOver(self):
        restartButton = button(self, (winWidth/2, winHeight/2), text="Back to Menu", center = True, colors = (colors.yellow, colors.white))
        buttons = pygame.sprite.Group(restartButton)
        while True:
            pygame.time.delay(50)
            
            self.runEvents()
            self.refresh()

            buttons.update()
            for btn in buttons:
                self.win.blit(btn.image, btn.rect)

            if restartButton.clicked:
                self.reset()
                break
            
            
            text1 = self.gameOverFont.render('Game Over', self.antialiasing, colors.dark(colors.red, 20))
            text2 = fonts['1'].render("Score: " + str(self.points), self.antialiasing, (colors.yellow))
            
            self.win.blit(text1, (50,50))
            self.win.blit(text2, (800, 70))
            
            pygame.display.update()

    def refresh(self, bg = False):
        if bg:
            self.win.blit(pygame.transform.scale(pygame.image.load(bg), (winWidth, winHeight)).convert(), (0, 0))
        else:
            self.win.fill((0, 0, 0))

#### Creates and runs game ####
game1 = game()
while __name__ == '__main__':
    game1.run()

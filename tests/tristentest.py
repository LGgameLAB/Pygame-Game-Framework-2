import pygame

from settings import *


pygame.init() # This loads the primary functions of pygame. You can still use some things without it but it loads the screen etc.

class player:
    def __init__(self,xy):
        self.speed = 0.3
        self.vel = pygame.Vector2(0,0)
        self.pos = pygame.Vector2(xy[0],xy[1])
        #self.image = pygame.image.load("download.png")
        #self.rect = pygame.Rect(self.pos.x,self.pos.y,self.image.get_width()/3,self.image.get_height()/3)
        #self.image = pygame.transform.scale(self.image,self.rect.size)

    def draw(self,win):
        #win.blit(self.image,self.pos)
        pygame.draw.rect(win,purple,(self.pos.x,self.pos.y,50,50))

    def update(self):
        self.move()

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.vel.x += self.speed
        if keys[pygame.K_a]:
            self.vel.x -= self.speed
        if keys[pygame.K_s]:
            self.vel.y += self.speed
        if keys[pygame.K_w]:
            self.vel.y -= self.speed

        lim = 5 # sets our limit
        self.vel *= 0.95 # slows the player down
        if self.vel.length() > 0.01: # We can't limit a 0 vector 
            self.vel.scale_to_length(max(-lim,min(self.vel.length(),lim)))
        self.pos += self.vel

def main(): # To make this like c we gonna have the main function to hold everything
    win = pygame.display.set_mode((winwidth, winheight))
    run = True
    p1 = player( ( 0,0 ) )
    clock = pygame.time.Clock()
    while run:
        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        win.fill(white) 
        
        # DO STUFF HERE
        clock.tick(fps)
        p1.update()
        p1.draw(win)
                
        pygame.display.update() # Essential display update command

main()
pygame.quit()
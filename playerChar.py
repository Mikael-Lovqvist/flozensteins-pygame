import pygame
import math
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 720
HERO_IMAGE = pygame.transform.scale(pygame.image.load(".\hero.png"), (15, 15))

def calculate_new_xy(old_xy,speed,angle_in_radians):
    #print("calcXY" + str(old_xy))
    new_x = old_xy[0] + (speed*math.cos(angle_in_radians))
    new_y = old_xy[1] + (speed*math.sin(angle_in_radians))
    return round(new_x), round(new_y)

class player(pygame.sprite.Sprite):
    def __init__(self,x,y, angle):
        self.dir = 0
        self.angle = 180
        self.speed = 0
        self.vel_x = 0
        self.vel_y = 0
        self.change_angle = 0
        self.health = 100
        self.x = x 
        self.y = y
        self.decel = False
        self.running = False
        self.mapID = 1
        a = math.radians(self.dir)
        pygame.sprite.Sprite.__init__(self)
        PlayerSprite = pygame.Surface([15,15], pygame.SRCALPHA)
        self.image = pygame.transform.scale(HERO_IMAGE,(15,15))
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(self.x,self.y))
#        self.image.fill((0,255,0))
        #shape = [(0,8), (3,0), (6,8)]
        #pygame.draw.lines(self.image,(255,0,0),False,shape, 4)

        self.collision = [False] * 9

        
        
    def update(self,speed,angle):
        #update after a move
        self.image = pygame.transform.rotate(HERO_IMAGE,math.degrees(-angle))
        #print(angle)
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(int(self.x),int(self.y)))
#       
        if self.decel == True:
            while self.speed < 0:
                self.speed = self.speed + 0.1
                if self.speed > 0.2:
                    self.speed = 0
            while self.speed > 0:
                self.speed = self.speed - 0.1
                if self.speed < 0.2:
                    self.speed = 0
            
                    
        self.rect = pygame.Rect([int(self.x),int(self.y),8,8])
        self.rect.center=calculate_new_xy(self.rect.center,int(self.speed),int(self.angle))
        #print(str(self.x) + " - " + str(self.y))
        self.surf = pygame.transform.rotate(self.original_image,self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.surf = pygame.transform.rotate(self.original_image,self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.angle += self.change_angle
        self.change_angle = 0
        self.angle = self.angle % 360
        self.vel_x = speed * math.cos(angle)
        self.vel_y = speed * math.sin(angle)
        self.y = self.y + self.vel_y
        self.x = self.x + self.vel_x
        if self.vel_x > 0:
            self.vel_x = self.vel_x * -0.1
        if self.vel_x < 0:
            self.vel_x = self.vel_x * 0.1
        if self.vel_y > 0:
            self.vel_y = self.vel_y * -0.1
        if self.vel_y < 0:
            self.vel_y = self.vel_y * 0.1
        if self.vel_y > 2:
            self.vel_y = 2
        if self.vel_x > 2:
            self.vel_x = 2
        if self.vel_y < -2:
            self.vel_y = -2
        if self.vel_x < -2:
            self.vel_x = -2
        return(self.rect)
    def checkHit(self, rect):
        self.collision[0] = rect.collidepoint(self.rect.topleft)
        self.collision[1] = rect.collidepoint(self.rect.topright)
        self.collision[2] = rect.collidepoint(self.rect.bottomleft)
        self.collision[3] = rect.collidepoint(self.rect.bottomright)

        self.collision[4] = rect.collidepoint(self.rect.midleft)
        self.collision[5] = rect.collidepoint(self.rect.midright)
        self.collision[6] = rect.collidepoint(self.rect.midtop)
        self.collision[7] = rect.collidepoint(self.rect.midbottom)

        self.collision[8] = rect.collidepoint(self.rect.center)
        correction = 1
        if self.running == True:
            correction = 2
        if self.collision[0] or self.collision[2] or self.collision[4]:
            self.x = self.x + correction

        if self.collision[1] or self.collision[3] or self.collision[5]:
            self.x = self.x - correction

        if self.collision[0] or self.collision[1] or self.collision[6]:
            self.y = self.y + correction

        if self.collision[2] or self.collision[3] or self.collision[7]:
            self.y = self.y - correction
        if self.x < 1:
            self.x = SCREEN_HEIGHT - 15
            self.mapID = self.mapID - 1000
        if self.y < 1:
            self.y = SCREEN_HEIGHT - 15
            self.mapID = self.mapID + 1
        if self.x > SCREEN_WIDTH - 15:
            self.x = 1
            self.mapID = self.mapID + 1000
        if self.y > SCREEN_HEIGHT - 10:
            self.y = 1
            self.mapID = self.mapID - 1
        
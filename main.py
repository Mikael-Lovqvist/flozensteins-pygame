import random
from OpenGL.GL import *
from pygame.locals import *
import sys
#sys.setrecursionlimit(2000)

from datetime import datetime
import time
from pygame import font
import pygame
import csv
import numpy as np
from numpy import loadtxt
import math


#import game components
import keyinput
import playerChar
import monsters
import maps
import pellet

from utils import load_image
import configuration as C

pygame.init()
basicfont = pygame.font.SysFont(None,20)

BLACK = (0,0,0)
WHITE = (255,255,255)
GREY = (128,128,128)
RED = (255,0,0)
GREEN = (0,255,0)
BROWN = (128,64,0)
BLUE = (0,0,128)
YELLOW = (128,128,0)
PURPLE = (255,0,255)

pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), OPENGL | DOUBLEBUF)
pygame.display.set_caption("tile_engine")
pygame.display.init()
info = pygame.display.Info()
pygame.mouse.set_visible(False)

# basic opengl configuration
glViewport(0, 0, info.current_w, info.current_h)
glDepthRange(0, 1)
glMatrixMode(GL_PROJECTION)
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glShadeModel(GL_SMOOTH)
glClearColor(0.0, 0.0, 0.0, 0.0)
glClearDepth(1.0)
glDisable(GL_DEPTH_TEST)
glDisable(GL_LIGHTING)
glDepthFunc(GL_LEQUAL)
glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
glEnable(GL_BLEND)

###
### Function to convert a PyGame Surface to an OpenGL Texture
### Maybe it's not necessary to perform each of these operations
### every time.
###
texID = glGenTextures(1)
def surfaceToTexture( pygame_surface ):
    global texID
    rgb_surface = pygame.image.tostring( pygame_surface, 'RGB')
    glBindTexture(GL_TEXTURE_2D, texID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    surface_rect = pygame_surface.get_rect()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, surface_rect.width, surface_rect.height, 0, GL_RGB, GL_UNSIGNED_BYTE, rgb_surface)
    glGenerateMipmap(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, 0)

#func to draw alpha'd rectangle
def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)

#create the clock
clock = pygame.time.Clock()

#create offscreen surface to render to
offscreen_surface = pygame.Surface((info.current_w, info.current_h))

MONSTER_IMAGE = load_image('monster.png', 20, 20)
WATER_IMAGE = load_image('water.png', 25, 25)
DIRT_IMAGE = load_image('dirt.png', 25, 25)
GRASS_IMAGE = load_image('grass.png', 25, 25)
STONE_IMAGE = load_image('stone.png', 25, 25)
SMALLSPLAT1 = load_image('smallsplat1.png', 5, 5)
SMALLSPLAT2 = load_image('smallsplat2.png', 5, 5)
SMALLSPLAT3 = load_image('smallsplat3.png', 5, 5)
BIGSPLAT1 = load_image('bigsplat1.png', 25, 25)
BIGSPLAT2 = load_image('bigsplat2.png', 25, 25)
BIGSPLAT3 = load_image('bigsplat3.png', 25, 25)
playerPositionX = 250
playerPositionY = 250
tileposx = 0
tileposy = 0


all_walls = pygame.sprite.Group()
all_players = pygame.sprite.Group()
all_monsters = pygame.sprite.Group()
all_bullets = pygame.sprite.Group()
all_terrain = pygame.sprite.Group()
all_splats = pygame.sprite.Group()


mapID = 1
#game classes and code
class wall(pygame.sprite.Sprite):
    def __init__(self,tileposx,tileposy,tileType):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([25,25])
        self.image.fill((128,128,128))
        self.x = tileposx
        self.y = tileposy
        self.tileType = tileType
        if self.tileType == 1:
            self.image = STONE_IMAGE
        else:
            self.image.fill(RED)
        self.rect = pygame.Rect([self.x,self.y,25,25])

class terrain(pygame.sprite.Sprite):
    def __init__(self,tileposx,tileposy,tileType):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([25,25])
        self.image.fill((128,128,128))
        self.x = tileposx
        self.y = tileposy
        self.tileType = tileType
        if self.tileType == 1:
            self.image.fill(GREY)
        elif self.tileType == 2:
            self.image = GRASS_IMAGE
        elif self.tileType == 3:
            self.image = DIRT_IMAGE
        elif self.tileType == 4:
            self.image.fill(WHITE)
        elif self.tileType == 5:
            self.image.fill(YELLOW)
        elif self.tileType == 6:
            self.image = WATER_IMAGE
        else:
            self.image.fill(RED)
        self.rect = pygame.Rect([self.x,self.y,25,25])

class splat(pygame.sprite.Sprite):
    def __init__(self,tileposx,tileposy,bigSplat):
        pygame.sprite.Sprite.__init__(self)
        if bigSplat != True:
            splatChooser = random.randint(0,2)
            if splatChooser == 0:
                self.image = pygame.transform.rotate(SMALLSPLAT1,random.randint(0,360))
            elif splatChooser == 1:
                self.image = pygame.transform.rotate(SMALLSPLAT2,random.randint(0,360))
            elif splatChooser == 2:
                self.image = pygame.transform.rotate(SMALLSPLAT3,random.randint(0,360))
            self.x = tileposx
            self.y = tileposy
            self.rect = pygame.Rect([self.x,self.y,10,10])
        elif bigSplat == True:
            self.image = BIGSPLAT1
            splatChooser = random.randint(0,2)
            if splatChooser == 0:
                self.image = pygame.transform.rotate(BIGSPLAT1,random.randint(0,360))
            elif splatChooser == 1:
                self.image = pygame.transform.rotate(BIGSPLAT2,random.randint(0,360))
            elif splatChooser == 2:
                self.image = pygame.transform.rotate(BIGSPLAT3,random.randint(0,360))
            self.x = tileposx
            self.y = tileposy
            self.rect = pygame.Rect([self.x,self.y,25,25])
#create objects, player, monster, level



PlayerOne = playerChar.player(100,100,0)
all_players.add(PlayerOne)



levelData = maps.loadMap(PlayerOne.mapID)
for item in levelData:
    x = item[0]
    y = item[1]
    tileType = item[2]
    if tileType != 1:
        all_terrain.add(terrain(x,y,tileType))
    elif tileType == 1:
        all_walls.add(wall(x,y,tileType))

numCritters = (len(all_walls) + len(all_terrain)) / 3
#if numCritters == 0:
#    numCritters = 10;
i = 0
while i < numCritters:
    i = i + 1
    randomMonster = monsters.randomMonster(random.randint(100,900),random.randint(100,600),0, MONSTER_IMAGE)
    all_monsters.add(randomMonster)

while True:
    if len(all_monsters) == 0:
        PlayerOne.score = PlayerOne.score + 1
        PlayerOne.health = 100
        numCritters = ((len(all_walls) + len(all_terrain)) / 3) * PlayerOne.score
        if numCritters == 0:
            numCritters = 10;
        i = 0
        while i < numCritters:
            i = i + 1
            randomMonster = monsters.randomMonster(random.randint(100,900),random.randint(100,600),0, MONSTER_IMAGE)
            all_monsters.add(randomMonster)
    #get key input
    keyinput.update(PlayerOne)
    if (PlayerOne.firing == True):
        pos = pygame.mouse.get_pos()
        mouse_x = pos[0]
        mouse_y = pos[1]
        #spawn shot
        #pistol
        if PlayerOne.weapon == 1:
            pew = pellet.Bullet((PlayerOne.x), (PlayerOne.y), mouse_x, mouse_y,PlayerOne.angle)
            all_bullets.add(pew)
            PlayerOne.firing = False

        #shotgun
        if PlayerOne.weapon == 2:
            i = 0
            while i < 5:
                i = i + 1
                pew = pellet.Bullet((PlayerOne.x), (PlayerOne.y), mouse_x, mouse_y,(PlayerOne.angle + random.uniform(-0.2,0.2)))
                all_bullets.add(pew)
                PlayerOne.firing = False

    if PlayerOne.mapID != mapID:


        mapID = PlayerOne.mapID
        levelData = maps.loadMap(PlayerOne.mapID)
        for item in all_walls:
            item.kill()
        for item in all_splats:
            item.kill()
        for item in all_terrain:
            item.kill()
        for item in levelData:
            x = item[0]
            y = item[1]
            tileSet = item[2]
            if tileSet != 1:
                all_terrain.add(terrain(x,y,tileSet))
            elif tileSet == 1:
               all_walls.add(wall(x,y,tileSet))
        for item in all_monsters:
            item.kill()

        i = 0
        numCritters = (len(all_walls)  + len(all_terrain))/ 10
        while i < numCritters:
            i = i + 1
            randomMonster = monsters.randomMonster(random.randint(100,900),random.randint(100,600),0, MONSTER_IMAGE)
            all_monsters.add(randomMonster)
    numText = basicfont.render(str(PlayerOne.score) + " pts | " + str(int(PlayerOne.health)) + " hp | mapID: " + str(mapID) + " | enemies: " + str(len(all_monsters)) + "/" + str(numCritters),True,WHITE)
    numTextRect = numText.get_rect()
    numTextRect.center = (500,20)

    #RENDER to offscreen_surface
    offscreen_surface.fill((0,0,0))

    for block in all_walls:
        PlayerOne.checkHit(block.rect)
    for monster in all_monsters:
        monster.update(0.5,monster.angle,PlayerOne.x,PlayerOne.y,all_walls)
        #PlayerOne.checkHit(monster.rect)
        if monster.bleeding == True:
            all_splats.add(splat(monster.x,monster.y,False))
            monster.bleeding = False
        if monster.health <= 0:
            all_splats.add(splat(monster.x,monster.y,True))
            monster.bleeding = False
        if monster.attacking == True:
            PlayerOne.health = PlayerOne.health - 1
            all_splats.add(splat(PlayerOne.x,PlayerOne.y,False))
            monster.attacking = False
    if PlayerOne.health <= 0:
        PlayerOne.mapID = 99999999
        PlayerOne.alive = False
    for bullet in all_bullets:
        bullet.update(all_walls,all_monsters)


    PlayerOne.update(PlayerOne.speed,PlayerOne.angle)



    all_terrain.draw(offscreen_surface)
    all_splats.draw(offscreen_surface)
    all_walls.draw(offscreen_surface)
    all_monsters.draw(offscreen_surface)
    all_players.draw(offscreen_surface)
    all_bullets.draw(offscreen_surface)

    draw_rect_alpha(offscreen_surface, (0,0,0, 64), numTextRect)
    #pygame.draw.rect(offscreen_surface,BLACK,numTextRect)
    offscreen_surface.blit(numText,numTextRect)

 # prepare to render the texture-mapped rectangle
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glDisable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)
    #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    #glClearColor(0, 0, 0, 1.0)

    # draw texture openGL Texture
    surfaceToTexture( offscreen_surface )
    glBindTexture(GL_TEXTURE_2D, texID)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(-1, 1)
    glTexCoord2f(0, 1); glVertex2f(-1, -1)
    glTexCoord2f(1, 1); glVertex2f(1, -1)
    glTexCoord2f(1, 0); glVertex2f(1, 1)
    glEnd()

    pygame.display.flip()
    clock.tick(120)

    #PlayerOne.rect = PlayerOne.update(PlayerOne.speed,PlayerOne.angle)

"""class mother des armes"""

from tkinter import E
import pygame
from src.tools.constant import PATH, IMPACT
from src.tools.tools import Vector2
from src.weapons.physique import *
from math import pi
import time
from src.mobs.MOTHER import BodyPartSprite

class WEAPON(pygame.sprite.Sprite):
    
    def __init__(self, id, target):
        super().__init__()
        self.image=pygame.image.load(PATH/"assets"/"weapons"/"sniper.png").convert_alpha()
        transColor = self.image.get_at((0,0))
        self.image.set_colorkey(transColor)
        self.image_bullet_r=pygame.image.load(PATH/"assets"/"weapons"/"bullet.png").convert_alpha()
        self.image_bullet_l=pygame.transform.flip(self.image_bullet_r, True, False)
        self.image_bullet=self.image_bullet_r
        transColor = self.image_bullet.get_at((0,0))
        self.image_bullet.set_colorkey(transColor)
        self.rect_bullet=self.image_bullet.get_rect()
        self.rect=self.image.get_rect()
        self.target=target
        self.id=id
        self.direction="left"
        self.angle=0
        self.is_firing=False
        self.start_firing=0
        self.v0=150
        self.h0=0
        self.x0=0
        self.rayon=20
        self.bullet_mask = BodyPartSprite((0,0),(self.rect_bullet.width, self.rect_bullet.height))
    
    def flip_pic(self, dir):
        self.direction=dir
        self.image=pygame.transform.flip(self.image, True, False)
        transColor = self.image.get_at((0,0))
        self.image.set_colorkey(transColor)

    def fire(self):
        if not self.is_firing:
            self.is_firing=True
            self.start_firing=time.time()
            self.h0=self.rect.y
            self.x0=self.rect.x
            self.rect_bullet.x=self.x0
            self.rect_bullet.y=self.h0
            self.bullet_direction=self.direction
            if self.bullet_direction=='right':
                self.image_bullet=self.image_bullet_r
            else:
                self.image_bullet=self.image_bullet_l
            transColor = self.image_bullet.get_at((0,0))
            self.image_bullet.set_colorkey(transColor)


    def update(self, map):
        
        if self.is_firing:
            t=time.time()-self.start_firing
            x=get_x(t, self.v0, self.angle)
            self.rect_bullet.y=get_y(x, self.v0, self.angle, self.h0)
            if self.bullet_direction=="left":
                x*=-1
            self.rect_bullet.x=x+self.x0
            if self.bullet_mask.collide(self.rect_bullet.topleft, map):
                self.is_firing=False
                ev=pygame.event.Event(IMPACT, {"x":self.rect_bullet.x, "y":self.rect_bullet.y, "radius":self.rayon})
                pygame.event.post(ev)
            elif self.rect_bullet.x<-300 or self.rect_bullet.x>map.rect.width+300 or self.rect_bullet.y<-300 or self.rect_bullet.y>map.rect.height+300:
                self.is_firing=False
            #print(t, self.rect_bullet.x, self.rect_bullet.y, self.h0, self.x0)
        if self.target.rigth_direction and self.direction=="left":
            self.flip_pic("right")
        elif not self.target.rigth_direction and self.direction=="right":
            self.flip_pic("left")
        if self.direction=="left":
            self.rect.x=self.target.rect.x-self.image.get_width()
            self.rect.y=self.target.rect.y+10
        else:
            self.rect.x=self.target.rect.x+self.target.image.get_width()
            self.rect.y=self.target.rect.y+10

        
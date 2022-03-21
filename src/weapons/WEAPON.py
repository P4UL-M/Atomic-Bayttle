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
        if id == "sniper":
            self.image=pygame.image.load(PATH/"assets"/"weapons"/"sniper.png").convert_alpha()
            self.image_bullet_r=pygame.image.load(PATH/"assets"/"weapons"/"bullet.png").convert_alpha()
            self.image_bullet_l=pygame.transform.flip(self.image_bullet_r, True, False)
            self.v0=130
            self.rayon=20
            self.base_image=self.image.copy()
        
        transColor = self.image.get_at((0,0))
        self.image.set_colorkey(transColor)
        
        self.image_bullet=self.image_bullet_r
        transColor = self.image_bullet.get_at((0,0))
        self.image_bullet.set_colorkey(transColor)
        self.rect_bullet=self.image_bullet.get_rect()
        self.rect=self.image.get_rect()
        self.target=target
        self.id=id
        self.direction="left"
        self.angle=0
        self.max_angle=1.8
        self.min_angle=-1.8
        self.is_firing=False
        self.start_firing=0
        self.h0=0
        self.x0=0
        self.angle_shoot=self.angle
        
        self.bullet_mask = BodyPartSprite((0,0),(self.rect_bullet.width, self.rect_bullet.height))
    
    def flip_pic(self, dir):
        self.direction=dir
        self.image=pygame.transform.flip(self.image, True, False)
        transColor = self.image.get_at((0,0))
        self.image.set_colorkey(transColor)
        self.base_image=pygame.transform.flip(self.base_image, True, False)
        self.base_image.set_colorkey(transColor)

    def aim(self,dir):
        i=0.1
        if dir=="up":
            if self.angle+i<self.max_angle:
                self.angle+=i
                if self.direction=="left":
                    ri = pygame.transform.rotate(self.base_image, -1*self.angle*10)
                else:
                    ri = pygame.transform.rotate(self.base_image, 1*self.angle*10)
                self.rect = ri.get_rect()
                self.image=ri
                transColor = self.image.get_at((0,0))
                self.image.set_colorkey(transColor)
        else:
            if self.angle-i>self.min_angle:
                self.angle-=i
                if self.direction=="left":
                    ri = pygame.transform.rotate(self.base_image, -1*self.angle*10)
                else:
                    ri = pygame.transform.rotate(self.base_image, 1*self.angle*10)
                
                self.rect = ri.get_rect()
                self.image = ri
                transColor = self.image.get_at((0,0))
                self.image.set_colorkey(transColor)
    def fire(self):
        if not self.is_firing:
            self.is_firing=True
            self.start_firing=time.time()
            self.h0=self.rect.y
            if self.angle<0:
                self.h0-=self.angle*10
            self.bullet_direction=self.direction
            if self.bullet_direction=='right':
                self.x0=self.rect.x+self.image.get_width()
                self.image_bullet=self.image_bullet_r
            else:
                self.x0=self.rect.x-self.target.image.get_width()+15
                self.image_bullet=self.image_bullet_l
            self.rect_bullet.x=self.x0
            self.rect_bullet.y=self.h0
            transColor = self.image_bullet.get_at((0,0))
            self.image_bullet.set_colorkey(transColor)    
            self.angle_shoot=self.angle

    def update(self, map):
        if self.is_firing:
            t=time.time()-self.start_firing
            x=get_x(t, self.v0, self.angle_shoot)
            self.rect_bullet.y=get_y(x, self.v0, self.angle_shoot, self.h0)
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
            self.rect.centerx=self.target.rect.x-self. base_image.get_width()+30
            self.rect.centery=self.target.rect.y+20-self.angle*2
        else:
            self.rect.centerx=self.target.rect.x+self.target.image.get_width()+15
            self.rect.centery=self.target.rect.y+20-self.angle*2

        
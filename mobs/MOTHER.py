import pygame
from math import sqrt
from tools.tools import Keyboard,Vector2,Axis
import tools.constant as tl

GAME = None

class BodyPartSprite(pygame.mask.Mask):
    def __init__(self, pos:tuple,size:tuple):
        super().__init__(size,True)
        self.pos = Vector2(*pos)
    
    def collide(self,pos:tuple,target:pygame.sprite.Sprite): 
        try:
            target.__getattribute__("rect")
        except:
            raise AttributeError("targe must have a mask to detect collision")

        x_off = target.rect.left - (pos[0]+self.pos.x)
        y_off = target.rect.top- (pos[1]+self.pos.y)
        return self.overlap(target.mask,(x_off,y_off))

class MOB(pygame.sprite.Sprite):

    def __init__(self, pos,size,group):
        super().__init__(group)
        
        self.rect = pygame.Rect(*pos,*size)
        self.inertia = Vector2(0,0)

        self.x_axis = Axis()
        self.y_axis = Axis()

        self.speed = 20

        self.grounded = False # vérification si au sol ou non
        self.in_action = False # en cas d'annimation spéciale

        # body part with position relative to the player position
        self.body_mask = BodyPartSprite((self.rect.width * 0.25,self.rect.height * 0.1),(self.rect.width * 0.5, self.rect.height*0.8))
        self.feet_mask = BodyPartSprite((self.rect.width * 0.25,self.rect.height * 0.7),(self.rect.width * 0.5, self.rect.height*0.3))
        self.head_mask = BodyPartSprite((self.rect.width * 0.25,0),(self.rect.width * 0.5, self.rect.height*0.3))
        self.body_left_mask = BodyPartSprite((0,self.rect.height * 0.4),(self.rect.width * 0.4, self.rect.height*0.3))
        self.body_right_mask = BodyPartSprite((self.rect.width * 0.6,self.rect.height * 0.4),(self.rect.width * 0.4, self.rect.height*0.3))    

    def move(self,target,serialized):
        try:
            self.__getattribute__("rect")
        except:
            raise AttributeError("MOB must have a rect to move")

        _dy = (self.y_axis*self.speed + self.inertia.y)*serialized
        _pos = Vector2(self.rect.left,self.rect.top + _dy)
        if self.body_mask.collide(_pos(),target):
            if self.head_mask.collide(_pos(),target) and _dy > 0:
                ... #TODO end animation here and other stuff
            elif self.feet_mask.collide(_pos(),target) and _dy < 0:
                ... #TODO end animation here and other stuff
                #TODO clip the perso on the ground
            else:
                pass
                #_dy = 0
        _dx = (self.x_axis*self.speed + self.inertia.x)*serialized
        _pos = Vector2(self.rect.left + _dx,self.rect.top + _dy)
        if self.body_mask.collide(_pos(),target):
            if self.body_left_mask.collide(_pos(),target) and _dx > 0:
                ... #TODO end animation here and other stuff
            elif self.body_right_mask.collide(_pos(),target) and _dx < 0:
                ... #TODO end animation here and other stuff
            else:
                pass
                #_dx = 0

        _finalPos = Vector2(self.rect.left + _dx,self.rect.top + _dy)
        self.rect.move_ip(_dx,_dy)

    def handle(self,event:pygame.event.Event): 
        """methode appele a chaque event"""
        match event.type:
            case tl.GRAVITY:
                if not self.grounded:
                    self.inertia.y += 9.81*event.serialized * 0.01
            case _:
                ...

    def update(self,map,serialized):
        self.move(map,serialized)

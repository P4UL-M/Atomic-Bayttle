import pygame
from math import sqrt,ceil
from tools.tools import Keyboard,Vector2,Axis
import tools.constant as tl

SCREEN = None
ft = pygame.font.SysFont("arial",32)

class BodyPartSprite(pygame.mask.Mask):
    def __init__(self, pos:tuple,size:tuple):
        super().__init__(size,True)
        self.pos = Vector2(*[ceil(i) for i in pos])
    
    def collide(self,pos:tuple,target:pygame.sprite.Sprite) -> bool: 
        try:
            target.__getattribute__("rect")
        except:
            raise AttributeError("targe must have a mask to detect collision")

        x_off = target.rect.left - (pos[0]+self.pos.x)
        y_off = target.rect.top- (pos[1]+self.pos.y)
        return self.overlap(target.mask,(x_off,y_off))!=None

    def collide_normal(self,pos:tuple,target:pygame.sprite.Sprite) -> Vector2:
        x = target.rect.left - (pos[0]+self.pos.x)
        y = target.rect.top- (pos[1]+self.pos.y)
        dx = self.overlap_area(target.mask, (x + 1, y)) - self.overlap_area(target.mask, (x - 1, y))
        dy = self.overlap_area(target.mask, (x, y + 1)) - self.overlap_area(target.mask, (x, y - 1))
        return Vector2(dx,dy)

class MOB(pygame.sprite.Sprite):

    def __init__(self, pos,size,group):
        super().__init__(group)
        
        self.rect = pygame.Rect(*pos,*size)
        self.inertia = Vector2(0,0)

        self.x_axis = Axis()
        self.y_axis = Axis()

        self.speed = 5
        self.actual_speed = 0
        self.gravity = 0.05

        self.grounded = False # vérification si au sol ou non
        self.in_action = False # en cas d'annimation spéciale

        # body part with position relative to the player position
        self.body_mask = BodyPartSprite((0,0),(self.rect.width, self.rect.height))
        self.feet_mask = BodyPartSprite((0,self.rect.height * 0.7),(self.rect.width, self.rect.height*0.3))
        self.head_mask = BodyPartSprite((0,0),(self.rect.width, self.rect.height*0.3))
        self.body_left_mask = BodyPartSprite((0,0),(self.rect.width * 0.4, self.rect.height))
        self.body_right_mask = BodyPartSprite((self.rect.width * 0.6,0),(self.rect.width * 0.4, self.rect.height))

    def move(self,target,serialized):
        try:
            self.__getattribute__("rect")
        except:
            raise AttributeError("MOB must have a rect to move")

        #* if mobs clip in the surface
        pygame.draw.rect(SCREEN,(0,0,0,0),pygame.Rect(0,0,1280,720))
        __dy,__dx = 0,0
        _pos = Vector2(self.rect.left,self.rect.top)
        if self.body_mask.collide(_pos(),target):
            _normal = self.body_mask.collide_normal(_pos(),target)
            self.inertia.x +=  _normal.x*0.025*self.speed; self.inertia.y += _normal.y*0.025*self.speed
            self.x_axis.value = 0
            self.y_axis.value = 0

        
        _dy = int((self.y_axis*self.speed + self.inertia.y)*serialized)
        _dx = int((self.x_axis*self.speed + self.inertia.x)*serialized)

        _pos = Vector2(self.rect.left + __dx ,self.rect.top + __dy)
        #* Y calculation
        _pos = Vector2(self.rect.left + __dx,self.rect.top + _dy + __dy)
        if self.body_mask.collide(_pos(),target):
            if self.head_mask.collide(_pos(),target) and _dy < 0:
                __ipos_l = Vector2(self.rect.left - _dy,self.rect.top + _dy)
                __ipos_r = Vector2(self.rect.left + _dy,self.rect.top + _dy)
                if not self.body_mask.collide(__ipos_l(),target) or not self.body_mask.collide(__ipos_r(),target):
                    if not self.body_mask.collide(__ipos_l(),target):
                        self.inertia.x -= _dy
                    if not self.body_mask.collide(__ipos_r(),target):
                        self.inertia.x += _dy
                else:
                    _dy = 0
                    self.inertia.y = 0
            elif self.feet_mask.collide(_pos(),target) and _dy > 0:
                _dy = 0
                self.grounded = True
                self.inertia.y = 0
                __ipos = Vector2(self.rect.left,self.rect.top + _dy)
                while not self.body_mask.collide(__ipos(),target):
                    _dy += 1
                    __ipos = Vector2(self.rect.left,self.rect.top + _dy)
                else:
                    _dy -= 1
            else:
                _dy = 0
                self.inertia.y = 0
                self.grounded = True
        else:
            self.grounded = False

        #* X calculation
        _pos = Vector2(self.rect.left + _dx + __dx,self.rect.top + _dy + __dy)
        if self.body_mask.collide(_pos(),target):
            if self.body_left_mask.collide(_pos(),target) and _dx < 0: # collision on left
                __ipos = Vector2(self.rect.left + _dx,self.rect.top + _dy - abs(_dx))
                if not self.body_mask.collide(__ipos(),target) and self.grounded:
                    _dy -= abs(_dx)
                else:
                    _dx = 0
                    __ipos = Vector2(self.rect.left + _dx,self.rect.top + _dy)
                    while not self.body_mask.collide(__ipos(),target):
                        _dx -= 1
                        __ipos = Vector2(self.rect.left + _dx,self.rect.top + _dy)
                    else:
                        _dx += 1
            elif self.body_right_mask.collide(_pos(),target) and _dx > 0: # collision on right
                __ipos = Vector2(self.rect.left + _dx,self.rect.top + _dy - abs(_dx))
                if not self.body_mask.collide(__ipos(),target) and self.grounded:
                    _dy -= abs(_dx)
                else:
                    _dx = 0
                    __ipos = Vector2(self.rect.left + _dx,self.rect.top + _dy)
                    while not self.body_mask.collide(__ipos(),target):
                        _dx += 1
                        __ipos.x += 1
                    else:
                        _dx -= 1
            else:
                _dx = 0
        
        self.actual_speed = sqrt(_dx**2 + _dy**2)
        self.rect.move_ip(_dx + __dx,_dy + __dy)

    def handle(self,event:pygame.event.Event): 
        """methode appele a chaque event"""
        match event.type:
            case tl.GRAVITY:
                if not self.grounded and self.inertia.y < self.speed*2:
                    self.inertia.y += 9.81*event.serialized*self.gravity
                if self.inertia.x != 0:
                    self.inertia.x += (0-self.inertia.x)/2
            case _:
                ...

    def update(self,map,serialized):
        self.move(map,serialized)

import pygame
from math import sqrt,ceil,pi,sin,cos
from tools.tools import Keyboard,Vector2,Axis
import tools.constant as tl
import time
import random

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
        self.height_mask = BodyPartSprite((self.rect.width*0.15,0),(self.rect.width*0.7, self.rect.height*1.2))
        self.side_mask = BodyPartSprite((0,self.rect.width*0.3),(self.rect.width, self.rect.height*0.4))

    def move(self,target,serialized, nbr_player):
        try:
            self.__getattribute__("rect")
        except:
            raise AttributeError("MOB must have a rect to move")

        #* if mobs clip in the surface
        __dy,__dx = 0,0
        _pos = Vector2(self.rect.left,self.rect.top)
        if self.body_mask.collide(_pos(),target):
            _normal = self.body_mask.collide_normal(_pos(),target)
            self.inertia.x +=  _normal.x*0.025*self.speed; self.inertia.y += _normal.y*0.025*self.speed
            self.x_axis.value = 0
            self.y_axis.value = 0
            
        _dy = int((self.y_axis*self.speed + self.inertia.y)*serialized)
        _dx = int((self.x_axis*self.speed + self.inertia.x)*serialized)
        _d = Vector2(_dx,_dy)
        self.actual_speed = _d.lenght

        _movements = [self.rect.width // 4 for i in range(int(self.actual_speed/(self.rect.width // 4)))] + [self.actual_speed%(self.rect.width // 4)]

        j = 0
        for i in _movements:
            if _d.arg != None: # arg is none we have no movement
                __d = _d.unity * i
                __d = self.collide_reaction(__d,i,target)
                self.rect.move_ip(*__d)
            else:
                __d = self.collide_reaction(Vector2(0,0),0,target)
                self.rect.move_ip(*__d)

    def collide_reaction(self,__d:Vector2,i:int,target):
        _n = self.body_mask.collide_normal((__d + self.rect.topleft)(),target)
        if _n.arg != None: # arg is none we have no collision
            if self.actual_speed > self.speed * 2 and __d.lenght > 0: #* boucing effect
                _angle = 2*_n.arg - __d.arg # the absolute angle of our new vector
                _dangle = __d.arg - _angle # the diff of angle between the two
                self.inertia.x = -(cos(_dangle)*__d.x + sin(_dangle)*__d.y)
                self.inertia.y = -(sin(_dangle)*__d.x + cos(_dangle)*__d.y)
                return Vector2(0,0)# break before movement to take account of new inertia
            #* counter of collision
            if _n.arg < -pi/4 and _n.arg > -3*pi/4 and self.height_mask.collide((__d + self.rect.topleft)(),target):
                self.inertia.y = 0
                self.grounded = True
                while self.body_mask.collide((__d + self.rect.topleft)(),target) and __d.y > 0:
                    __d.y -= 1
                _test = (__d + self.rect.topleft); _test.y -= i
                if not self.body_mask.collide(_test(),target) and abs(__d.x) > 0 and self.body_mask.collide((__d + self.rect.topleft)(),target):
                    __d.y -= i
            elif _n.arg > pi/5 and _n.arg < 4*pi/5 and self.height_mask.collide((__d + self.rect.topleft)(),target):
                _test = (__d + self.rect.topleft); _test.x -= i*1.2
                if not self.body_mask.collide(_test(),target):
                    __d.y -= i*1.2
                _test = (__d + self.rect.topleft); _test.x += i*1.2
                if not self.body_mask.collide(_test(),target):
                    __d.y += i*1.2
                else:
                    self.inertia.y = 0
                    while self.body_mask.collide((__d + self.rect.topleft)(),target) and __d.y < 0:
                        __d.y += 1
            elif self.side_mask.collide((__d + self.rect.topleft)(),target):
                while self.body_mask.collide((__d + self.rect.topleft)(),target) and abs(__d.x) < i:
                    __d.x += 1 if _n.x > 0 else -1
            else:
                if _n.arg < 0 and _n.arg > -pi:
                    __d.x += (1 if _n.x > 0 else -1)*i
                while self.body_mask.collide((__d + self.rect.topleft)(),target) and abs(__d.lenght) < i:
                    __d.x += 1 if _n.x > 0 else -1
        else:
            self.grounded = False
        if not self.body_mask.collide((__d + self.rect.topleft)(),target):
            return __d
        else:
            return Vector2(0,0)

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

    def update(self,map,serialized, nbr_player):
        self.move(map,serialized, nbr_player)

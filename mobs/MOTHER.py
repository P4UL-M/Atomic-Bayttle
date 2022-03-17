import pygame
from math import sqrt,ceil,pi,sin,cos
from tools.tools import Keyboard,Vector2,Axis
import tools.constant as tl

class BodyPartSprite(pygame.mask.Mask):
    def __init__(self, pos:tuple,size:tuple):
        super().__init__(size,True)
        self.pos = Vector2(*[ceil(i) for i in pos])
    
    def collide(self,pos:tuple,target:pygame.sprite.Sprite) -> bool: 
        try:
            target.__getattribute__("rect")
        except:
            raise AttributeError("target must have a mask to detect collision")

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
        self.life_multiplicator = 1

        self.grounded = False # vérification si au sol ou non

        # body part with position relative to the player position
        self.body_mask = BodyPartSprite((0,0),(self.rect.width, self.rect.height))
        self.feet = BodyPartSprite((self.rect.width*0.15,self.rect.height*0.6),(self.rect.width*0.7, self.rect.height*0.8))
        self.head = BodyPartSprite((0,self.rect.height*-0.2),(self.rect.width, self.rect.height*0.5))
        self.side_mask = BodyPartSprite((0,self.rect.width*0.3),(self.rect.width, self.rect.height*0.4))
        self.mask = self.body_mask # for collision with other and projectil

    def move(self,target,serialized):
        try:
            self.__getattribute__("rect")
        except:
            raise AttributeError("MOB must have a rect to move")
            
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
        if _n.arg != None: #* arg is not none then we have collision
            if self.actual_speed > self.speed * 2 and __d.lenght > 0: # boucing effect
                _angle = 2*_n.arg - __d.arg # the absolute angle of our new vector
                _dangle = __d.arg - _angle # the diff of angle between the two
                self.inertia.x = -(cos(_dangle)*__d.x + sin(_dangle)*__d.y)*self.life_multiplicator
                self.inertia.y = -(sin(_dangle)*__d.x + cos(_dangle)*__d.y)*2*self.life_multiplicator
            elif _n.arg < -pi/4 and _n.arg > -3*pi/4 and self.feet.collide((__d + self.rect.topleft)(),target): # collision on feet
                self.inertia.y = 0
                self.grounded = True
                while self.body_mask.collide((__d + self.rect.topleft)(),target) and __d.y > 0: # unclip
                    __d.y -= 1
                _test = (__d + self.rect.topleft); _test.y -= i # test climbing
                if not self.body_mask.collide(_test(),target) and abs(__d.x) > 0 and self.body_mask.collide((__d + self.rect.topleft)(),target):
                    __d.y -= i
            elif _n.arg > pi/4 and _n.arg < 3*pi/4 and self.head.collide((__d + self.rect.topleft)(),target): # collision of head
                _NE = (__d + self.rect.topleft); _NE.x -= i*1.2
                _NW = (__d + self.rect.topleft); _NW.x += i*1.2
                if not self.body_mask.collide(_NE(),target): # test displacement on right
                    __d.x -= i*1.2
                elif not self.body_mask.collide(_NW(),target): # test displacement on left
                    __d.x += i*1.2
                else: # no alternative then stop the jump
                    self.inertia.y = 0
                    while self.body_mask.collide((__d + self.rect.topleft)(),target) and __d.y < 0:
                        __d.y += 1
            elif self.side_mask.collide((__d + self.rect.topleft)(),target): # collision on side
                if _n.x > 0:
                    while self.body_mask.collide((__d + self.rect.topleft)(),target) and __d.x < 0:
                        __d.x += 1
                    if not self.grounded: # strange bug clip surface while flying
                        self.inertia.x += self.speed
                elif _n.x < 0:
                    while self.body_mask.collide((__d + self.rect.topleft)(),target) and __d.x > 0:
                        __d.x -= 1
                    if not self.grounded: # strange bug clip surface while flying
                        self.inertia.x -= self.speed
            else: # collision undefined
                while self.body_mask.collide((__d + self.rect.topleft)(),target) and __d.lenght < self.speed*3:
                    __d += _n.unity
                    self.body_mask.collide_normal((__d + self.rect.topleft)(),target)
        else: #* else no collison so no operation
            self.grounded = False
        if not self.body_mask.collide((__d + self.rect.topleft)(),target):
            return __d
        else:
            return Vector2(0,0) # in case the reaction fail or like with boucing

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

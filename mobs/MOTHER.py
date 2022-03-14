import pygame
from math import sqrt,ceil,pi
from tools.tools import Keyboard,Vector2,Axis
import tools.constant as tl

CAMERA = None
font = pygame.font.SysFont("arial",20)

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
        
        _dy = int((self.y_axis*self.speed + self.inertia.y)*serialized)
        _dx = int((self.x_axis*self.speed + self.inertia.x)*serialized)
        _d = Vector2(_dx,_dy)
        self.actual_speed = _d.lenght
        _direction = _d.unity

        if self.actual_speed > self.rect.width or self.actual_speed >self.rect.height:
            ...

        for i in range(1): ...
        _n = self.body_mask.collide_normal((_d + self.rect.topleft)(),target)
        if _n.arg != None:
            print(pygame.time.get_ticks(),_n.arg / pi,(_d + self.rect.topleft))
            if self.actual_speed > self.speed * 1.5 and False:
                #todo si possible récup point de collision, analyser la surface pour chopper la normal à celle ci et calculer un bouncing réaliste
                self.inertia.x += _n.x * self.actual_speed
                self.inertia.y += _n.y * self.actual_speed
            else:
                if _n.arg < -pi/4 and _n.arg > -3*pi/4:
                    while self.body_mask.collide((_d + self.rect.topleft)(),target) and _d.y < 0:
                        _d.y -= 1
                    self.inertia.y = 0
                    self.grounded = True
                    print("hey")
                else:
                    while self.body_mask.collide((_d + self.rect.topleft)(),target) and _d.y < self.actual_speed:
                        _d += _n.unity
                    self.inertia += _n.unity
        else:
            self.grounded = False

        pygame.draw.rect(CAMERA._screen_UI,(0,0,0,0),pygame.Rect(0,0,1200,1000))
        pygame.draw.line(CAMERA._screen_UI,(255,0,0),(800,200),(800 - _n.x,200 - _n.y))
        if _n.arg:
            CAMERA._screen_UI.blit(font.render(str(round(_n.arg/pi,2)),True,(0,0,0)),(800,300))
        CAMERA.cache = False

        self.rect.move_ip(*_d)

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

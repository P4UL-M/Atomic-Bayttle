import pygame
import random
from pygame.locals import *
from src.tools.tools import Vector2,sprite_sheet
import src.tools.constant as tl
from src.tools.constant import PATH

class Particule(pygame.sprite.Sprite):
    """ MAIN CLASS OF THE SCRIPT"""
    def __init__(self, lifetime,position:Vector2,range,direction:Vector2,speed,gravity):
        super().__init__()
        self.lifetime = lifetime*random.uniform(0.9, 1.1)
        self.position = Vector2(position.x + random.randrange(-range,range), position.y)
        self.direction = Vector2(direction.x + random.randrange(-1,1),direction.y + random.randrange(-1,1))
        self.gravity = gravity
        self.speed = speed
        
        self.image = pygame.transform.scale(pygame.image.load(PATH / "assets" / "particle.png"),(3,3))
        self.image = pygame.transform.rotate(self.image,random.randrange(0,90))
        li_loss = random.randrange(0,55); li_teinte = random.randrange(0,25)
        self.image.fill((255-li_loss,255-li_loss-li_teinte,255-li_loss-li_teinte))
        self.rect = self.image.get_rect(topleft=self.position())
    
    def move(self,serialized):
        try:
            self.__getattribute__("rect")
        except:
            raise AttributeError("MOB must have a rect to move")

        _dx = self.direction.x * self.speed * serialized
        _dy = self.direction.y * self.speed * serialized
        self.rect.move_ip(_dx,_dy)

    def handle(self,event:pygame.event.Event): 
        """methode appele a chaque event"""
        match event.type:
            case tl.GRAVITY:
                if self.gravity:
                    self.direction.y -= 9.81/self.speed

    def update(self,serialized,*args,**kargs):
        if self.lifetime < 0:
            self.kill()
        else:
            self.lifetime -= 1
            self.move(serialized)

class AnimatedParticule(pygame.sprite.Sprite):
    def __init__(self, spritesheet:sprite_sheet,lifetime:int,position:Vector2,range,direction:Vector2,speed,gravity):
        super().__init__()
        self.lifetime = lifetime
        self.position = Vector2(position.x + random.randrange(-range,range), position.y)
        self.direction = Vector2(direction.x + random.randrange(-1,1),direction.y + random.randrange(-1,1))
        self.gravity = gravity
        self.speed = speed
        self.frame = 0
        self.dframe = (spritesheet.x_nb * spritesheet.y_nb)/lifetime
        
        self.spritesheet = spritesheet
        self.image = pygame.transform.rotate(self.image,random.randrange(0,90))
        li_loss = random.randrange(0,55); li_teinte = random.randrange(0,25)
        self.image.fill((255-li_loss,255-li_loss-li_teinte,255-li_loss-li_teinte))
        self.rect = self.image.get_rect(topleft=self.position())
    
    @property
    def image(self):
        return self.spritesheet[self.frame]

    def move(self,serialized):
        try:
            self.__getattribute__("rect")
        except:
            raise AttributeError("MOB must have a rect to move")

        _dx = self.direction.x * self.speed * serialized
        _dy = self.direction.y * self.speed * serialized
        self.rect.move_ip(_dx,_dy)

    def handle(self,event:pygame.event.Event): 
        """methode appele a chaque event"""
        match event.type:
            case tl.GRAVITY if self.gravity:
                self.direction.y -= 9.81/self.speed

    def update(self,serialized,*args,**kargs):
        if self.lifetime >= self.frame:
            self.kill()
        else:
            self.frame += self.dframe
            self.move(serialized)
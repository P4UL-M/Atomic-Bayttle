import pygame
import random
from pygame.locals import *
import pathlib
from tools.tools import Vector2
import tools.constant as tl

PATH = pathlib.Path(__file__).parent.parent

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
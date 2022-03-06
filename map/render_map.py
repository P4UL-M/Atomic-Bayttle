import pygame
from pygame.locals import *
from tools.tools import Vector2

class Map(pygame.sprite.Sprite):
    def __init__(self, path):
        super().__init__()
        self.image = pygame.image.load(path).convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.water_level = self.image.get_height()
    
    def add_damage(self,_pos:Vector2,radius): #pass damage and update mask
        pygame.draw.circle(self.image,(0,0,0,0),_pos(),radius)
        self.mask = pygame.mask.from_surface(self.image)

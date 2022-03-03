import pygame
from pygame.locals import *

class Map(pygame.sprite.Sprite):
    def __init__(self, path):
        super().__init__()
        self.image=pygame.image.load(path).convert(32,pygame.SRCALPHA + pygame.HWSURFACE + pygame.HWACCEL)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
    
    def add_damage(): #pass damage and update mask
        ...
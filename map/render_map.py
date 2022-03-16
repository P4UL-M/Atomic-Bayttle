import pygame
from pygame.locals import *
from tools.tools import Vector2,sprite_sheet,animation_Manager

class Map(pygame.sprite.Sprite):
    def __init__(self, PATH):
        super().__init__()
        self.image = pygame.image.load(PATH / "assets" / "environnement" / "map.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.water_level = self.image.get_height() - 30
        self.water_target = self.image.get_height() - 30

        self.water_manager = animation_Manager()
        _water_idle = sprite_sheet(PATH / "assets" / "environnement" / "water_idle.png",(448,252))
        _water_idle.config(self.rect.size)
        _water_agitated = sprite_sheet(PATH / "assets" / "environnement" / "water_agitated.png",(448,252))
        _water_agitated.config(self.rect.size)
        self.water_manager.add_annimation("idle",_water_idle,40)
        self.water_manager.add_annimation("agitated",_water_agitated,40)
        self.water_manager.load("idle")

    def add_damage(self,_pos:Vector2,radius): #pass damage and update mask
        pygame.draw.circle(self.image,(0,0,0,0),_pos(),radius)
        self.mask = pygame.mask.from_surface(self.image)
        self.water_target -= 1
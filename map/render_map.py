from logging import exception
from math import ceil
import pygame

class Map(pygame.sprite.Sprite):
    def __init__(self, x, y, directory):
        super().__init__()
        self.x=x
        self.y=y
        self.image=pygame.image.load(f"{directory}\\assets\\map.png").convert_alpha()
        transColor = self.image.get_at((0,0))
        self.image.set_colorkey(transColor)
        self.image=pygame.transform.scale(self.image, (self.image.get_width()*2, self.image.get_height()*2)).convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.w=self.rect.w
        self.h=self.rect.h
    
    def add_damage(): #pass damage and update mask
        ... 


class RenderMap: #! useless
    def __init__(self, screen_width, screen_height, directory):
        """cf la documentation de pytmx"""
        self.directory=directory
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.map=Map(0, 0, directory)
    
    def get_height(self):
        """return the height of the map in coordonates"""
        return self.map.image.get_height()

    def get_width(self):
        """return the width of the map in coordonates"""
        return self.map.image.get_width()
 
    def render(self, surface, cam_x, cam_y, scroll_rect):
        """called all tick => blit only the visible tiles (compare to the position of the camera) to 'surface'"""

        new_x = surface.get_width()/2 - scroll_rect.x
        new_y = surface.get_height()/2 - scroll_rect.y
        
        surface.blit(self.map.image, (new_x, new_y))
from logging import exception
from math import ceil
import pytmx
import random
import pygame

class MapSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, directory):
        super(MapSprite, self).__init__()
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

class RenderMap:
    def __init__(self, screen_width, screen_height, directory):
        """cf la documentation de pytmx"""
        self.directory=directory
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # self.image_map=pygame.image.load(f"{directory}\\assets\\map.png")
        # self.image_map=pygame.transform.scale(self.image_map, (self.image_map.get_width()*2, self.image_map.get_height()*2)).convert_alpha()
        # transColor = self.image_map.get_at((0,0))
        # self.image_map.set_colorkey(transColor)
        # self.mask=pygame.mask.from_surface(self.image_map)

        self.map=MapSprite(0, 0, directory)

        self.zoom=2
    
    def get_height(self):
        """return the height of the map in coordonates"""
        # we remove the 2 empty map that are on the top and on the bot of the map
        return self.map.image.get_height()

    def get_width(self):
        """return the width of the map in coordonates"""
        # we remove the 2 empty map that are on the left and on the right of the map
        return self.map.image.get_width()
 
    def render(self, surface, cam_x, cam_y, scroll_rect):
        """called all tick => blit only the visible tiles (compare to the position of the camera) to 'surface'"""

        # computation of the minimal and maximals coordinates that the tiles need to have to be visible
        # y_min = ceil((cam_y-self.screen_height/2)/(self.tm.tileheight*self.zoom))-2
        # y_max = ceil((cam_y+self.screen_height/2)/(self.tm.tileheight*self.zoom))+1
        # x_min = ceil((cam_x-self.screen_width/2)/(self.tm.tilewidth*self.zoom))-2
        # x_max = ceil((cam_x+self.screen_width/2)/(self.tm.tilewidth*self.zoom))+1
        # if y_min<0: y_min=0
        # elif y_min>self.tm.height: y_min=self.tm.height
        # if x_min<0: x_min=0
        # elif x_min>self.tm.width: x_min=self.tm.width
        # #bliting those tiles in the surface in parameter
        # y = y_min
        # x = x_min
        # for ligne in self.liste_tile[y_min:y_max]:
        #     for img in ligne[x_min:x_max]:
        #         if img != None:
        #             surface.blit(img, (self.screen_width/2 + x*self.tm.tilewidth*self.zoom - cam_x, self.screen_height/2 + y*self.tm.tileheight*self.zoom - cam_y))
        #         x+=1
        #     x=x_min
        #     y += 1
        
        new_x = surface.get_width()/2 - scroll_rect.x
        new_y = surface.get_height()/2 - scroll_rect.y
        
        surface.blit(self.map.image, (new_x, new_y))
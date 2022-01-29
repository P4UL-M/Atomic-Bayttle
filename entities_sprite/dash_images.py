import pygame
import time
from pygame.locals import *

class Dash_images(pygame.sprite.Sprite):
    """ class affichant une image du joueur quand il dash pour une courte duree"""
    def __init__(self, x, y ,image, c):
        super().__init__()
        self.id = "image_dash"
        self.image = image 
        # l'image devient transparente
        self.image.fill((255,255,255, 125), special_flags=BLEND_RGBA_MULT) 
        self.position = [x,y]
        self.rect = self.image.get_rect()
        self.t1 = time.time()
        # temps d'apparition
        self.cooldown = 0.5 + c
        self.body = pygame.Rect(0,0,self.rect.width * 0.3, self.rect.height)
        
    def update(self):
        self.rect.topleft = self.position
        self.body.midbottom = self.rect.midbottom
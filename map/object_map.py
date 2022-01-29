import pygame
import time
import random

class Object_map(pygame.sprite.Sprite):
    
    def __init__(self, zoom, id, x, y, directory, nbr_image,compteur_image_max, directory_assets, name_image, coefficient, complement_x, complement_y, c, d):
        super().__init__()
        self.coord_map=[d, c]
        self.id=id
        self.directory=directory
        directory_assets=directory_assets
        self.images = {
            "nbr_image":nbr_image,
            "compteur_image_max":compteur_image_max,
            "images":{},
        }
        for i in range(1,nbr_image+1):
            self.images["images"][str(i)] = pygame.image.load(f'{self.directory}\\{directory_assets}\\{name_image}{i}.png').convert_alpha()
            self.images["images"][str(i)] = pygame.transform.scale(self.images["images"][str(i)], (round(self.images["images"][str(i)].get_width()*zoom*coefficient), round(self.images["images"][str(i)].get_height()*zoom*coefficient))).convert_alpha()
        self.image=self.images["images"]["1"]
        self.position=[x-self.image.get_width()/2 +complement_x*zoom, y-self.image.get_height()+1+complement_y*zoom]
        self.dt = 17
        self.speed_dt = 1
        # images
        self.compteur_image = 0
        self.current_image = 1
        self.rect=self.image.get_rect()
        self.rect.x=self.position[0]
        self.rect.y=self.position[1]
    
    def update_tick(self, dt):
        """i created a multiplicator for the mouvements that based on 60 fps (clock.tick() = 17) because the original
        frame rate is 60, and so the mouvements are speeder when the game is lagging so when
        the game has a lower frame rate, same for animations but it doesnt work perfectly for animations"""
        self.dt = dt
        self.speed_dt = round(self.dt/17)
    
    def update_animation(self):
        # changement de l'image tout les X ticks
        if self.compteur_image < self.images["compteur_image_max"]:
            self.compteur_image += 1*self.speed_dt
        else:
            self.compteur_image = 0
            # si l'image en cours est la derniere on re passe a la 1ere, sinon on passe a la suivante
            if self.current_image < self.images["nbr_image"]:
                self.current_image += 1
            else:
                self.current_image = 1
            self.image = self.images["images"][str(self.current_image)]
            transColor = self.image.get_at((0,0))
            self.image.set_colorkey(transColor)

    def update(self):
        self.update_animation()
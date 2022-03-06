import pygame
import os
from pygame.locals import *
from map.render_map import Map
from entities_sprite.particule import Particule
from mobs.player import Player
#from map.object_map import Object_map
import tools.constant as tl
from tools.tools import sprite_sheet,animation_Manager
from weapons.physique import *
import pathlib

GAME = None
CAMERA = None
PATH = pathlib.Path(__file__).parent

class Partie:
    def __init__(self):
        self.map = Map(PATH / "assets" / "environnement" / "map.png")

        self.manager = animation_Manager()
        _animation = sprite_sheet(PATH / "assets" / "environnement" / "background_sheet.png",(448,252))
        _animation.config(self.map.image.get_size())
        self.manager.add_annimation("main",_animation,10)
        self.manager.load("main")

        self.mobs = pygame.sprite.Group()
        self.group_particle = pygame.sprite.Group()
        self.group_object=pygame.sprite.Group()
        
        self.checkpoint=(100, 50) # the swpan point à remplacer après par le system
        self.camera_target:pygame.sprite.Sprite = None
        pygame.mouse.set_visible(False)
    
    @property
    def bg(self):
        return self.manager.surface

    def add_player(self, team):
        player = Player("j1",self.checkpoint,tl.TEAM[team]["idle"],team,self.mobs)
        self.mobs.add(player)

    """pas au role de game
    def interact_object_map(self, id):
        if id =="mortier":
            print("coucou")"""

    def Update(self):
        """ fonction qui update les informations du jeu"""
        pygame.event.post(pygame.event.Event(tl.GRAVITY,{"serialized":GAME.serialized}))
        # event 
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    raise SystemExit
                case _:
                    for mob in self.mobs:
                        mob.handle(event)
  
        self.mobs.update(self.map,GAME.serialized,CAMERA,self.group_particle)
        self.group_particle.update(GAME.serialized)

        # render
        self.Draw()

        return

    def Draw(self):
        _surf = self.bg.copy()
        _surf.blit(self.map.image,(0,0)) 
        self.mobs.draw(_surf)
        self.group_object.draw(_surf)
        self.group_particle.draw(_surf)
        CAMERA._off_screen = _surf

    def test_parabole(self):
        x0=self.mortier.position[0] + self.mortier.image.get_width()/2
        h0=self.mortier.position[1] + self.mortier.image.get_width()/2
        v0=8.2
        from math import pi
        a=pi/4

        for t in range(1, 1000):
            x=get_x(t/10, v0, a)
            y=get_y(x, v0, a, h0)
            x=x*v0+x0
            if self.scroll_rect.x - (self.screen.get_width()/2) <= x <= self.scroll_rect.x + (self.screen.get_width()/2) and \
                self.scroll_rect.y - (self.screen.get_height()/2) <= y <= self.scroll_rect.y + (self.screen.get_height()/2):
                    new_x=self.screen.get_width()/2 + x - self.scroll_rect.x
                    new_y = self.screen.get_height()/2 + y - self.scroll_rect.y
                    pygame.draw.circle(self.screen, (255, 0, 0), (new_x, new_y), 3)
        
        a=pi/6            
        for t in range(1, 1000):
            x=get_x(t/10, v0, a)
            y=get_y(x, v0, a, h0)
            x=x*v0+x0
            if self.scroll_rect.x - (self.screen.get_width()/2) <= x <= self.scroll_rect.x + (self.screen.get_width()/2) and \
                self.scroll_rect.y - (self.screen.get_height()/2) <= y <= self.scroll_rect.y + (self.screen.get_height()/2):
                    new_x=self.screen.get_width()/2 + x - self.scroll_rect.x
                    new_y = self.screen.get_height()/2 + y - self.scroll_rect.y
                    pygame.draw.circle(self.screen, (0, 255, 0), (new_x, new_y), 3)
        
        
        a=(2*pi)/6
        for t in range(1, 1000):
            x=get_x(t/10, v0, a)
            y=get_y(x, v0, a, h0)
            x=x*v0+x0
            if self.scroll_rect.x - (self.screen.get_width()/2) <= x <= self.scroll_rect.x + (self.screen.get_width()/2) and \
                self.scroll_rect.y - (self.screen.get_height()/2) <= y <= self.scroll_rect.y + (self.screen.get_height()/2):
                    new_x=self.screen.get_width()/2 + x - self.scroll_rect.x
                    new_y = self.screen.get_height()/2 + y - self.scroll_rect.y
                    pygame.draw.circle(self.screen, (0, 0, 255), (new_x, new_y), 3)

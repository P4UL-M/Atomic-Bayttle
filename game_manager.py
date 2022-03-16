import pygame
import os
from pygame.locals import *
from map.render_map import Map
from entities_sprite.particule import Particule
from mobs.player import Player
from map.object_map import Object_map
import tools.constant as tl
from tools.tools import sprite_sheet,animation_Manager,MixeurAudio,Vector2
from weapons.physique import *
import pathlib
import time
import random
from math import sqrt

GAME = None
CAMERA = None
PATH = pathlib.Path(__file__).parent

class Partie:
    def __init__(self):
        self.map = Map(PATH)

        self.manager = animation_Manager()
        _animation = sprite_sheet(PATH / "assets" / "environnement" / "background_sheet.png",(448,252))
        _animation.config(self.map.image.get_size())
        self.manager.add_annimation("main",_animation,10)
        self.manager.load("main")

        self.mobs = pygame.sprite.Group()
        self.group_particle = pygame.sprite.Group()
        self.group_object=pygame.sprite.Group()
        
        self.checkpoint=(100, 50) # the swpan point à remplacer après par le system
        pygame.mouse.set_visible(False)
        self.nbr_player=1
        self.cooldown_tour=10
        self.timer_tour=0

    @property
    def bg(self):
        return self.manager.surface

    def add_player(self, name,team):
        player = Player(name,(0, 0),tl.TEAM[team]["idle"],team,self.mobs)
        self.mobs.add(player)

    def place_player(self):
        w=self.map.image.get_width()
        h=self.map.image.get_height()
        for player in self.mobs.sprites():
            continuer=True
            while continuer:
                player.rect.x=random.randint(0, w)
                player.rect.y=random.randint(0, h)
                _pos = Vector2(player.rect.left,player.rect.top)
                if player.body_mask.collide(_pos(),self.map):
                    while player.rect.y>0 and player.body_mask.collide(_pos(),self.map):
                        player.rect.y-=1
                        _pos = Vector2(player.rect.left,player.rect.top)
                    if player.rect.y>0:
                        continuer=False
                    else:
                        continue
                else:
                    while player.rect.y<h and not player.body_mask.collide(_pos(),self.map):
                        player.rect.y+=1
                        _pos = Vector2(player.rect.left,player.rect.top)
                    if player.rect.y<h:
                        continuer=False
                    else:
                        continue
                for p in self.mobs.sprites():
                    if p.name!=player.name:
                        if sqrt((player.rect.x-p.rect.x)**2 + (player.rect.y-p.rect.y)**2)<100:
                            continuer=True


    
    def add_playerList_into_players(self):
        
        for sprite in self.mobs.sprites():
            sprite.list_others=[]
            for sprite2 in self.mobs.sprites():
                if sprite2.name!=sprite.name:
                    sprite.list_others.append(sprite2)

    def add_object(self,name,pos, path):
        self.group_object.add(Object_map(name,pos, path))

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
                    for obj in self.group_object:
                        obj.handle(event)
        if time.time()-self.timer_tour>self.cooldown_tour:
            self.timer_tour=time.time()
            self.nbr_player+=1
            if self.nbr_player>len(self.mobs.sprites()):
                self.nbr_player=1

        self.mobs.update(self.map,GAME.serialized,CAMERA,self.group_particle, self.nbr_player)
        self.group_particle.update(GAME.serialized)

        MixeurAudio.update_musique()

        if self.map.water_target < self.map.water_level:
            self.map.water_level -= 0.1*GAME.serialized
            self.map.water_manager.load("agitated")
        else:
            self.map.water_manager.load("idle")

        # render
        self.Draw()

        return

    def Draw(self): 
        _surf = self.bg.copy()
        _surf.blit(self.map.image,(0,0))
        _surf.blit(self.map.water_manager.surface,(0,self.map.water_level))
        self.group_object.draw(_surf)
        self.mobs.draw(_surf) 
        self.group_particle.draw(_surf)
        CAMERA._off_screen = _surf.convert()

    def test_parabole(self): #! a réécrire sans le zoom
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
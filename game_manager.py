import pygame
from pygame.locals import *
from map.render_map import Map
from entities_sprite.particule import Particule
from mobs.player import Player
from map.object_map import Object_map
import tools.constant as tl
from tools.tools import sprite_sheet,animation_Manager,MixeurAudio,Vector2,cycle
from weapons.physique import *
import pathlib
from math import sqrt

GAME = None
CAMERA = None
PATH = pathlib.Path(__file__).parent

FONT = pygame.font.SysFont("Arial",24)

class Partie:
    def __init__(self):
        self.map = Map(PATH)

        self.manager = animation_Manager()
        _animation = sprite_sheet(PATH / "assets" / "environnement" / "background_sheet.png",(448,252))
        _animation.config(self.map.image.get_size())
        self.back_cloud = pygame.transform.scale(pygame.image.load(PATH /  "assets" / "environnement" / "cloud_back_sheet.png"),(self.map.image.get_width()*2,self.map.image.get_height()))
        self.front_cloud = pygame.transform.scale(pygame.image.load(PATH /  "assets" / "environnement" / "cloud_front_sheet.png"),(self.map.image.get_width()*2,self.map.image.get_height()))
        self.manager.add_annimation("main",_animation,10)
        self.manager.load("main")

        self.mobs = pygame.sprite.Group()
        self.group_particle = pygame.sprite.Group()
        self.group_object=pygame.sprite.Group()
        
        self.checkpoint=(100, 50) # the swpan point à remplacer après par le system
        pygame.mouse.set_visible(False)
        self.cooldown_tour=5000
        self.timer_tour=pygame.time.get_ticks()

    @property
    def bg(self):
        _surf = self.manager.surface
        _surf.blit(self.back_cloud, (-((pygame.time.get_ticks()/100)%(self.map.image.get_width())),0))
        _surf.blit(self.front_cloud, (-((pygame.time.get_ticks()/50)%(self.map.image.get_width())),0))
        return _surf

    def add_player(self, name,team,lock=False):
        player = Player(name,self.checkpoint,tl.TEAM[team]["idle"],team,self.mobs)
        player.lock = lock
        self.actual_player = cycle(*[mob.name for mob in self.mobs.sprites()])
        self.mobs.add(player)

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
                case tl.ENDTURN:
                    self.timer_tour = pygame.time.get_ticks()
                    self.actual_player += 1
                    for mob in self.mobs.sprites():
                        if mob.name == str(self.actual_player):
                            mob.lock = False
                        else:
                            mob.lock = True
                case _:
                    for mob in self.mobs:
                        mob.handle(event)
                    for obj in self.group_object:
                        obj.handle(event)

        self.mobs.update(self.map,self.mobs.sprites(),GAME.serialized,CAMERA,self.group_particle)
        self.group_particle.update(GAME.serialized)

        MixeurAudio.update_musique()

        if self.timer_tour + self.cooldown_tour < pygame.time.get_ticks():
            ev = pygame.event.Event(tl.ENDTURN)
            pygame.event.post(ev)

        if self.map.water_target < self.map.water_level:
            self.map.water_level -= 0.1*GAME.serialized
            self.map.water_manager.load("agitated")
        else:
            self.map.water_manager.load("idle")

        # render
        CAMERA._screen_UI.fill((0,0,0,0))
        timer = (self.timer_tour + self.cooldown_tour - pygame.time.get_ticks())//1000 + 1
        CAMERA._screen_UI.blit(FONT.render(str(timer),1,(0,0,0)),(640,50))
        CAMERA.cache = False
        self.Draw()

        return

    def Draw(self): 
        _surf = self.bg.copy()
        _surf.blit(self.map.cave_bg.image,self.map.cave_bg.rect.topleft)
        _surf.blit(self.map.image,(0,0))
        _surf.blit(self.map.water_manager.surface,(0,self.map.water_level))
        self.mobs.draw(_surf) 
        self.group_object.draw(_surf)
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
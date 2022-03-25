import pygame
from pygame.locals import *
from src.map.render_map import Map
from src.mobs.player import Player
from src.map.object_map import Object_map
import src.tools.constant as tl
from src.tools.tools import MixeurAudio,cycle,Vector2
from src.weapons.physique import *
from src.weapons.WEAPON import WEAPON

GAME = None
CAMERA = None

FONT = pygame.font.SysFont("Arial",24)

class Partie:
    def __init__(self):
        self.map = Map()

        self.mobs = pygame.sprite.Group()
        self.group_particle = pygame.sprite.Group()
        self.group_object=pygame.sprite.Group()
        
        self.checkpoint=(100, 50) # the swpan point à remplacer après par le system
        pygame.mouse.set_visible(False)
        self.cooldown_tour=15000
        self.timer_tour=pygame.time.get_ticks()

    def add_player(self, name,team,lock=False):
        player = Player(name,self.checkpoint,tl.TEAM[team]["idle"],team,self.mobs, "sniper")
        player.lock = lock
        self.actual_player = cycle(*[mob.name for mob in self.mobs.sprites()])
        if "j2" in player.name:
            player.rect.topleft = (1200,600)
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
                case tl.DEATH:
                    CAMERA.zoom = 1
                    self.map.water_target = self.map.rect.height - 30
                    for mob in self.mobs.sprites():
                        if mob.name == event.name:
                            mob.respawn(self.checkpoint[1])
                case tl.IMPACT:
                    self.map.add_damage(Vector2(event.x, event.y),event.radius)
                    for mob in self.mobs:
                        mob.handle(event)
                    for obj in self.group_object:
                        obj.handle(event)
                case _:
                    for mob in self.mobs:
                        mob.handle(event)
                    for obj in self.group_object:
                        obj.handle(event)

        self.mobs.update(self.map,self.mobs.sprites(),GAME.serialized,CAMERA,self.group_particle,self.mobs)
        self.group_particle.update(GAME.serialized)

        MixeurAudio.update_musique()

        if self.timer_tour + self.cooldown_tour < pygame.time.get_ticks():
            ev = pygame.event.Event(tl.ENDTURN)
            pygame.event.post(ev)

        self.map.update(GAME.serialized)

        # render
        CAMERA._screen_UI.fill((0,0,0,0))
        timer = (self.timer_tour + self.cooldown_tour - pygame.time.get_ticks())//1000 + 1
        CAMERA._screen_UI.blit(FONT.render(str(timer),1,(0,0,0)),(640,50))

        #todo à virer après
        for player in self.mobs.sprites():
            if type(player)== Player:
                if not player.lock:
                    CAMERA._screen_UI.blit(FONT.render(str(int(player.life_multiplicator * 100)) + "%",1,(255,0,0)),(50,50))

        CAMERA.cache = False
        self.Draw()

        return

    def Draw(self): 
        _surf = pygame.Surface(self.map.image.get_size(),flags=pygame.SRCALPHA)
        _surf.blit(self.map.cave_bg.image,self.map.cave_bg.rect.topleft)
        _surf.blit(self.map.image,(0,0))
        self.mobs.draw(_surf)
        for player in self.mobs.sprites():
            if type(player)==Player:
                _surf.blit(player.current_weapon.image,player.current_weapon.rect)
        self.group_particle.draw(_surf)
        self.group_object.draw(_surf)
        _surf.blit(self.map.water_manager.surface,(0,self.map.water_level))
        CAMERA._off_screen = _surf

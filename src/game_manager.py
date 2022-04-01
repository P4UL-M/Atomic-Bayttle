import pygame
from pygame.locals import *
from src.map.render_map import Map
from src.mobs.player import Player
from src.map.object_map import Object_map
import src.tools.constant as tl
from src.tools.tools import MixeurAudio, cycle, Vector2, sprite_sheet
from src.game_effect.particule import AnimatedParticule
from src.weapons.physique import *
from src.weapons.WEAPON import WEAPON
from src.game_effect.cinematic import *

GAME = None
CAMERA = None

FONT = pygame.font.SysFont("Arial", 24)


class Partie:
    def __init__(self):
        self.map = Map()

        self.mobs = pygame.sprite.Group()
        self.group_particle = pygame.sprite.Group()
        self.group_object = pygame.sprite.Group()

        # the swpan point à remplacer après par le system
        self.checkpoint = (100, 50)
        pygame.mouse.set_visible(False)
        self.cooldown_tour = 15000

        self.timeline = timeline()

    @property
    def players(self):
        return [mob for mob in self.mobs.sprites() if type(mob) == Player]

    def add_player(self, name, team, lock=False):
        player = Player(name, self.checkpoint,
                        tl.TEAM[team]["idle"], team, self.mobs, "sniper")
        player.lock = lock
        self.actual_player = cycle(*[mob.name for mob in self.mobs.sprites()])
        if "j2" in player.name:
            player.rect.topleft = (1200, 600)
        self.mobs.add(player)
        self.timeline.actions = []
        self.timeline.add_action(
            turn(str(self.actual_player), duration=self.cooldown_tour))

    def add_object(self, name, pos, path):
        self.group_object.add(Object_map(name, pos, path))

    def Update(self):
        """ fonction qui update les informations du jeu"""
        self.timeline.update(GAME, CAMERA)

    def Draw(self):
        _surf = pygame.Surface(self.map.image.get_size(),
                               flags=pygame.SRCALPHA)
        _surf.blit(self.map.cave_bg.image, self.map.cave_bg.rect.topleft)
        _surf.blit(self.map.image, (0, 0))
        self.mobs.draw(_surf)
        for player in self.mobs.sprites():
            if type(player) == Player:
                _surf.blit(player.weapon_manager.current_weapon.image,
                           player.weapon_manager.current_weapon.rect)
        self.group_particle.draw(_surf)
        self.group_object.draw(_surf)
        _surf.blit(self.map.water_manager.surface, (0, self.map.water_level))
        CAMERA._off_screen = _surf

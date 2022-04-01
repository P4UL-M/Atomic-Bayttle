import pygame
from pygame.locals import *
from src.map.render_map import Map
from src.mobs.player import Player
from src.map.object_map import Object_map
import src.tools.constant as tl
from src.tools.tools import MixeurAudio, Cycle, Vector2, sprite_sheet, Keyboard
from src.game_effect.particule import AnimatedParticule
from src.weapons.physique import *
from src.tools.constant import EndPartie
from src.weapons.WEAPON import WEAPON
from src.game_effect.cinematic import *
import random

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
        self.checkpoint = Vector2(100, 50)
        pygame.mouse.set_visible(False)
        self.cooldown_tour = 15000

        self.timeline = timeline()
        self.cycle_players = Cycle()

    @property
    def players(self):
        return [mob for mob in self.mobs.sprites() if type(mob) == Player]

    @property
    def actual_player(self):
        for player in self.players:
            if player.name == str(self.cycle_players):
                return player

    def add_player(self, name, team, lock=False):
        player = Player(name, self.checkpoint + Vector2(random.randint(0, 1200), 0), tl.TEAM[team]["idle"], team, self.mobs, "sniper")
        player.lock = lock
        self.cycle_players = Cycle(*[mob.name for mob in self.mobs.sprites()])
        self.mobs.add(player)
        self.timeline.actions = []
        self.timeline.add_action(Turn(self.actual_player, duration=self.cooldown_tour))

    def add_object(self, name, pos, path):
        self.group_object.add(Object_map(name, pos, path))

    def Update(self):
        """ fonction qui update les informations du jeu"""
        pygame.event.post(pygame.event.Event(
            tl.GRAVITY, {"serialized": GAME.serialized}))
        # event
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    raise SystemExit
                case tl.ENDTURN:
                    self.timeline.next(GAME, CAMERA, _type=Turn)
                case tl.DEATH:
                    if event.player.visible:
                        self.map.water_target = self.map.rect.height - 30
                        self.timeline.add_action(Death(event.player), asyncron=True)
                        self.timeline.add_action(Respawn(event.player))
                        if event.player == self.actual_player:
                            self.timeline.next(GAME, CAMERA, _type=Turn)
                case tl.IMPACT:
                    self.map.add_damage(
                        Vector2(event.x, event.y), event.radius)
                    if event.particle:
                        self.group_particle.add(event.particle)
                    for mob in self.mobs:
                        mob.handle(event, GAME, CAMERA)
                    for obj in self.group_object:
                        obj.handle(event, GAME, CAMERA)
                case _:
                    for mob in self.mobs:
                        mob.handle(event, GAME, CAMERA)
                    for obj in self.group_object:
                        obj.handle(event, GAME, CAMERA)
        if Keyboard.pause.is_pressed:
            raise EndPartie

        self.timeline.update(GAME, CAMERA)
        self.group_particle.update(GAME.serialized)
        self.map.update(GAME.serialized)
        MixeurAudio.update_musique()

        self.Draw()

    def Draw(self):
        _surf = pygame.Surface(self.map.image.get_size(), flags=pygame.SRCALPHA)
        _surf.blit(self.map.cave_bg.image, self.map.cave_bg.rect.topleft)
        _surf.blit(self.map.image, (0, 0))
        self.mobs.draw(_surf)
        for player in self.mobs.sprites():
            if type(player) == Player:
                if player.weapon_manager.current_weapon.visible:
                    _surf.blit(player.weapon_manager.current_weapon.image, player.weapon_manager.current_weapon.rect)
        self.group_particle.draw(_surf)
        self.group_object.draw(_surf)
        _surf.blit(self.map.water_manager.surface, (0, self.map.water_level))
        CAMERA._off_screen = _surf

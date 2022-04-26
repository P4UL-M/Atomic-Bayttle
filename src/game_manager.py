import pygame
from pygame.locals import *
from src.map.render_map import Map
from src.mobs.player import Player
from src.map.object_map import Object_map
import src.tools.constant as tl
from src.tools.tools import MixeurAudio, Cycle, Vector2, Keyboard, SizedList
from src.game_effect.particule import AnimatedParticule
from src.weapons.physique import *
from src.tools.constant import EndPartie
from src.weapons.WEAPON import WEAPON
from src.game_effect.cinematic import *

GAME = None
CAMERA = None

FONT = pygame.font.SysFont("Arial", 24)
TEAM = {}


class Partie:
    def __init__(self):
        self.map = Map()

        self.mobs = pygame.sprite.Group()
        self.group_particle = pygame.sprite.Group()
        self.group_object = pygame.sprite.Group()

        # the swpan point à remplacer après par le system
        self.checkpoint = Vector2(100, 50)
        self.checkpoints = {"j1.1": Vector2(160, 50), "j1.2": Vector2(400, 50), "j2.1": Vector2(1030, 50), "j2.2": Vector2(1235, 50)}
        pygame.mouse.set_visible(False)

        self.timeline = timeline()
        self.timeline.add_link(Turn, TurnTransition)
        self.timeline.add_link(TurnTransition, Turn)
        self.last_players = SizedList(4)

        self.turn_length = 15000

    @property
    def players(self) -> list[Player]:
        return [mob for mob in self.mobs.sprites() if type(mob) is Player]

    @property
    def actual_player(self):
        for player in self.players:
            if player.name == str(self.cycle_players):
                return player

    def add_player(self, name, team, lock=False):
        TEAM[name] = team
        player = Player(name, self.checkpoints[name], tl.TEAM[team]["idle"], team, self.mobs, "sniper")
        player.lock = lock
        self.cycle_players = Cycle(*[mob.name for mob in self.mobs.sprites()])
        self.mobs.add(player)
        self.last_players += player
        self.timeline.purge()
        self.timeline.add_action(Turn(GAME, CAMERA))

    def add_object(self, name, pos, path):
        self.group_object.add(Object_map(name, pos, path))

    def Update(self):
        CAMERA._screen_UI.fill((0, 0, 0, 0))
        CAMERA.cache = False
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
                    self.map.water_target = self.map.rect.height - 30
                    if event.player.life > 0:
                        self.timeline.add_action(Death(event.player), asyncron=True)
                        self.timeline.add_next(Respawn(event.player), 1)
                    else:
                        event.player.kill()
                        self.cycle_players.delete(name=event.player.name)
                case tl.IMPACT:
                    self.map.add_damage(Vector2(event.x, event.y), event.radius)
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

        # check end game
        names = ["j2" if ("j2" in mob.name) else "j1" for mob in self.players]
        if "j1" not in names or "j2" not in names and self.timeline.current_action_type != TurnTransition:
            raise EndPartie(TEAM[self.players[0].name], [name for name in TEAM.values() if name != TEAM[self.players[0].name]][0])

        self.Draw()

    def Draw(self):
        _surf = pygame.Surface(self.map.image.get_size(), flags=pygame.SRCALPHA)
        _surf.blit(self.map.cave_bg.image, self.map.cave_bg.rect.topleft)
        _surf.blit(self.map.image, (0, 0))
        self.mobs.draw(_surf)
        for player in self.mobs.sprites():
            if type(player) is Player:
                if player.weapon_manager.current_weapon.visible:
                    _surf.blit(player.weapon_manager.current_weapon.image, player.weapon_manager.current_weapon.rect)
        self.group_particle.draw(_surf)
        self.group_object.draw(_surf)
        _surf.blit(self.map.water_manager.surface, (0, self.map.water_level))
        CAMERA._off_screen = _surf

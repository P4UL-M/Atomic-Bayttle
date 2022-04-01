import pygame
from src.tools.constant import EndAction
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

FONT = pygame.font.SysFont("Arial", 24)


class Action:
    def __init__(self, duration=None):
        self.duration = duration
        self.time = ...
        self.__start_time = ...
        self.__update = ...

    def update(self, *args, **kwargs):
        if self.duration is not None:
            if self.time is ...:
                self.__start_time = pygame.time.get_ticks()
            self.time = self.duration - \
                (pygame.time.get_ticks() - self.__start_time)
        else:
            self.time = 1
        if self.time <= 0:
            raise EndAction()
        else:
            self.__update__(*args, **kwargs)

    def setup(self, *arg, **kargs): ...

    def clean(self, *arg, **kargs): ...

    def __update__(self): ...


class timeline:
    def __init__(self):
        self.actions: list[Action] = []
        self.__current_action = None

    def add_action(self, action):
        self.actions.append(action)

    def update(self, *args, **kwargs):
        if self.__current_action is None:
            self.__current_action = self.actions.pop(0)
            self.__current_action.setup(*args, **kwargs)
        try:
            self.__current_action.update(*args, **kwargs)
        except EndAction:
            self.__current_action.clean(*args, **kwargs)
            self.__current_action = None


class turn(Action):
    def __init__(self, player, duration=None):
        super().__init__(duration)
        self.player = player

    def __update__(self, GAME, CAMERA):
        GM = GAME.partie
        pygame.event.post(pygame.event.Event(
            tl.GRAVITY, {"serialized": GAME.serialized}))
        # event
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    raise SystemExit
                case tl.ENDTURN:
                    raise EndAction
                case tl.DEATH:
                    GM.timeline.add_action(Death(str(GM.actual_player)))
                    GM.timeline.add_action(Respawn(str(GM.actual_player)))
                    raise EndAction
                case tl.IMPACT:
                    GM.map.add_damage(
                        Vector2(event.x, event.y), event.radius)
                    if event.particle:
                        GM.group_particle.add(event.particle)
                    for mob in GM.mobs:
                        mob.handle(event, GAME, CAMERA)
                    for obj in GM.group_object:
                        obj.handle(event, GAME, CAMERA)
                case _:
                    for mob in GM.mobs:
                        mob.handle(event, GAME, CAMERA)
                    for obj in GM.group_object:
                        obj.handle(event, GAME, CAMERA)

        GM.mobs.update(GAME, CAMERA)
        GM.group_particle.update(GAME.serialized)

        MixeurAudio.update_musique()

        GM.map.update(GAME.serialized)

        # render
        CAMERA._screen_UI.fill((0, 0, 0, 0))
        timer = self.time // 1000 + 1
        CAMERA._screen_UI.blit(FONT.render(
            str(timer), 1, (0, 0, 0)), (640, 50))

        # todo à virer après
        for player in GM.mobs.sprites():
            if type(player) == Player:
                if not player.lock:
                    CAMERA._screen_UI.blit(FONT.render(
                        str(int(player.life_multiplicator * 100)) + "%", 1, (255, 0, 0)), (50, 50))

        CAMERA.cache = False
        GM.Draw()

    def setup(self, GAME, CAMERA):
        GM = GAME.partie
        for player in GM.players:
            player.lock = not player.name == self.player

    def clean(self, GAME, CAMERA):
        GM = GAME.partie
        GM.actual_player += 1
        GM.timeline.add_action(turn(str(GM.actual_player), duration=GM.cooldown_tour))


class Respawn(Action):
    def __init__(self, player, duration=5000):
        super().__init__(duration)
        self.player = player

    def setup(self, GAME, CAMERA):
        GM = GAME.partie
        for player in GM.players:
            if player.name == self.player:
                player.rect.topleft = GM.checkpoint()
                player.visible = False
                player.weapon_manager.visible = False
                break

    def __update__(self, GAME, CAMERA):
        GM = GAME.partie
        for event in pygame.event.get():
            ...
        GM.Draw()

    def clean(self, GAME, CAMERA):
        GM = GAME.partie
        for player in GM.players:
            if player.name == self.player:
                player.visible = True
                player.weapon_manager.visible = True
                break


class transition(Action):
    def __init__(self, duration=None):
        super().__init__(duration)


class Death(Action):
    def __init__(self, player, duration=1500):
        super().__init__(duration)
        self.player = player

    def __update__(self, GAME, CAMERA):
        GM = GAME.partie
        for event in pygame.event.get():
            ...

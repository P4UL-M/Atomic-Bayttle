"""
Atomic Bay'ttle
Paul Mairesse, Axel Loones, Louis Le Meilleur, Joseph Bénard, Théo de Aranjo
This file contain the definition of the main timeline of the game
"""
from __future__ import annotations
import pygame
from src.tools.constant import EndAction
from pygame.locals import *
from src.mobs.player import Player
import src.tools.constant as tl
from src.tools.tools import Vector2, sprite_sheet, Keyboard, ScreenSize
from src.game_effect.particule import AnimatedParticule, Particule
from src.weapons.physique import *
from src.game_effect.UI import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game import *

FONT = pygame.font.SysFont("Arial", 24)


class Action:
    def __init__(self, duration=None):
        self.duration = duration
        self.time = ...
        self._start_time = ...

    def update(self, *arg, **kargs):
        def func(*arg, **kargs):
            # time calculation
            if self.duration is not None:
                if self.time is ...:
                    self._start_time = pygame.time.get_ticks()
                self.time = self.duration - (pygame.time.get_ticks() - self._start_time)
            else:
                self.time = 1
            # update
            if self.time <= 0:
                raise EndAction()
            else:
                self.__update__(*arg, **kargs)
        self.setup(*arg, **kargs)
        func(*arg, **kargs)
        self.update = func

    def setup(self, *arg, **kargs): ...

    def clean(self, *arg, **kargs): ...

    def __update__(self): ...


class timeline:
    def __init__(self):
        self.actions: list[Action] = []
        self.async_actions: list[Action] = []
        self.__current_action = None
        self.__links = {}

    @property
    def next_action_type(self):
        if self.actions:
            return type(self.actions[0])
        else:
            return None

    @property
    def current_action_type(self):
        if self.__current_action:
            return type(self.__current_action)
        else:
            return None

    def add_action(self, action, asyncron=False):
        if not asyncron:
            self.actions.append(action)
        else:
            self.async_actions.append(action)

    # method to add action on top of the timeline
    def add_next(self, action, index=0):
        if index > len(self.actions):
            self.actions.append(action)
        else:
            self.actions.insert(index, action)

    def update(self, *args, **kwargs):
        if self.__current_action is None:
            self.__current_action = self.actions.pop(0)
        try:
            self.__current_action.update(*args, **kwargs)
        except EndAction:
            self.__current_action.clean(*args, **kwargs)
            if type(self.__current_action) in self.__links:
                self.add_action(self.__links[type(self.__current_action)](*args, **kwargs))
            self.__current_action = None
        for action in self.async_actions:
            try:
                action.update(*args, **kwargs)
            except EndAction:
                action.clean(*args, **kwargs)
                self.async_actions.remove(action)

    def next(self, GAME, CAMERA, _type=None):
        if self.__current_action and (not _type or type(self.__current_action) is _type):
            self.__current_action.clean(GAME, CAMERA)
            if type(self.__current_action) in self.__links:
                self.add_action(self.__links[type(self.__current_action)](GAME, CAMERA))
            self.__current_action = None

    def purge(self):
        self.actions.clear()
        self.async_actions.clear()

    def add_link(self, _from, _to):
        self.__links[_from] = _to


class Turn(Action):
    def __init__(self, GAME: Game, CAMERA: Camera):
        GM = GAME.partie
        super().__init__(GM.turn_length)
        for player in GM.players:
            if player not in GM.last_players:
                self.player = player
                break
        else:
            self.player = GM.last_players[0]

    def __update__(self, GAME: Game, CAMERA: Camera):
        GM = GAME.partie
        GM.mobs.update(GAME, CAMERA)

        if not self.player.visible:
            raise EndAction()

        if self.player.input_lock:
            self._start_time = pygame.time.get_ticks()

        # render
        CAMERA._screen_UI.blit(heart(self.player.life, 2).image, (12, 12))

        numbers = [int(a) for a in str(int(self.player.life_multiplicator * 100))]

        if len(numbers) > 2:
            CAMERA._screen_UI.blit(digit(numbers[0], 2).image, (12, 34))
        if len(numbers) > 1:
            CAMERA._screen_UI.blit(digit(numbers[-2], 2).image, (12 + (len(numbers) - 2) * 22, 34))
        CAMERA._screen_UI.blit(digit(numbers[-1], 2).image, (34 + (len(numbers) - 2) * 22, 34))
        CAMERA._screen_UI.blit(digit("%", 2).image, (56 + (len(numbers) - 2) * 22, 34))
        timer = [int(a) for a in str(self.time // 1000 + 1)]
        if len(timer) > 1:
            CAMERA._screen_UI.blit(digit(timer[len(timer) - 2], 2).image, (720 // 2 - 33 + (len(timer) - 1) * 22, 12))
        CAMERA._screen_UI.blit(digit(timer[len(timer) - 1], 2).image, (720 // 2 + (len(timer) - 1) * 11, 12))

    def setup(self, GAME: Game, CAMERA: Camera):
        GM = GAME.partie
        self.player.input_lock = True
        self.player.weapon_manager.visible = True
        self.player.weapon_manager.reload()
        for player in GM.players:
            player.lock = player != self.player

    def clean(self, GAME: Game, CAMERA: Camera):
        GM = GAME.partie
        self.player.lock = True
        GM.last_players += self.player


class Respawn(Action):
    def __init__(self, player: Player, duration=10000):
        super().__init__(duration)
        self.player: Player = player
        self.interract_up = False

    def setup(self, GAME: Game, CAMERA: Camera):
        GM = GAME.partie
        self.player.rect.topleft = GM.checkpoint()
        self.player.visible = True
        self.player.phatom = True
        self.player.respawn()
        CAMERA.zoom = 1.1

    def __update__(self, GAME: Game, CAMERA: Camera):
        GM = GAME.partie

        self.player.x_axis.update(Keyboard.right.is_pressed, Keyboard.left.is_pressed)
        if self.player.x_axis.value > 0:
            self.player.right_direction = True
        elif self.player.x_axis.value < 0:
            self.player.right_direction = False
        self.player.rect.x += self.player.x_axis * 1 * GAME.serialized * 10
        self.player.rect.x = min(max(self.player.rect.x, 100), GM.map.rect.width - self.player.rect.width - 100)

        for mob in GM.mobs.sprites():
            mob.update(GAME, CAMERA)

        # self.player.weapon_manager.update(self.player, GAME, CAMERA)
        # * CAMERA Update of the player
        x, y = CAMERA.to_virtual(ScreenSize.resolution.x / 2, ScreenSize.resolution.y / 2)
        _x, _y = (self.player.rect.left, self.player.rect.top)
        CAMERA.x += (_x - x) * 0.0001
        CAMERA.y += (_y - y) * 0.0001

        if Keyboard.interact.is_pressed:
            if self.interract_up:
                raise EndAction()
        else:
            self.interract_up = True

    def clean(self, GAME: Game, CAMERA: Camera):
        GM = GAME.partie
        self.player.phatom = False
        self.player.life -= 1

        _sprite = pygame.sprite.Sprite()
        _sprite.rect = GM.map.image.get_rect(topleft=(0, 0))
        _sprite.mask = GM.map.mask.copy()
        for player in GM.players:
            if not player.phatom and player.visible and player is not self.player:
                _sprite.mask.draw(player.mask, player.rect.topleft)
        while self.player.body_mask.collide(self.player.rect, _sprite):
            self.player.rect.x += 1


class Death(Action):
    def __init__(self, player: Player, duration=1500):
        super().__init__(duration)
        self.player: Player = player

    def setup(self, GAME: Game, CAMERA: Camera):
        GM = GAME.partie
        size = (28, 33)
        sp = sprite_sheet(tl.PATH / "assets" / "kraken" / "idle1.png", size)
        factor = (GM.map.rect.height - GM.map.water_level) / size[1]
        factor = max(3, factor)
        sp.config((size[0] * factor, size[1] * factor))
        if self.player.body_mask.collide(self.player.rect.topleft, GM.map):
            GM.group_particle.add(AnimatedParticule(sp, 15, Vector2(self.player.rect.left, GM.map.rect.height - size[1] * factor), 1, Vector2(1, 1), 0, False))
        else:
            raise EndAction()

    def __update__(self, GAME: Game, CAMERA: Camera):
        GM = GAME.partie
        if pygame.time.get_ticks() % 50 == 0:
            GM.group_particle.add(Particule(40, Vector2(self.player.rect.centerx, self.player.rect.bottom), 2, Vector2(0, -1), 0.5, Color(255, 255, 255), False))


class TurnTransition(Action):
    def __init__(self, GAME: Game, CAMERA: Camera):
        super().__init__()
        self.player: Player = GAME.partie.last_players[-1]
        self.state = {}
        self.check = 0

    def __update__(self, GAME: Game, CAMERA: Camera):
        GM = GAME.partie
        _state = {}
        for mob in GM.mobs:
            _state[mob.name] = mob.rect.topleft

        check = len(self.state) != 0
        for key, value in _state.items():
            if key not in self.state:
                check = False
                break
            elif value != self.state[key]:
                check = False
                break
        check = len(GM.timeline.async_actions) == 0 and check

        x, y = CAMERA.x, CAMERA.y
        _x, _y = (0, 0)
        Cx = CAMERA.x + (_x - x) * 0.0005
        Cy = CAMERA.y + (_y - y) * 0.0005
        # * Effect of dezoom relatif to speed
        Cz = CAMERA.zoom + (1 - CAMERA.zoom) * 0.05
        CAMERA.Update(Cx, Cy, Cz)

        if Keyboard.end_turn.is_pressed or (check and self.check > 1):
            raise EndAction()
        else:
            self.state = _state
            GM.mobs.update(GAME, CAMERA)
            if check:
                self.check += 1
            else:
                self.check = 0

    def clean(self, *arg, **kargs):
        self.player.weapon_manager.visible = False

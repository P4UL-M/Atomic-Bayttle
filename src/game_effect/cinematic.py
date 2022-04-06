import pygame
from src.tools.constant import EndAction
import pygame
from pygame.locals import *
from src.map.render_map import Map
from src.mobs.player import Player
from src.map.object_map import Object_map
import src.tools.constant as tl
from src.tools.tools import MixeurAudio, Cycle, Vector2, sprite_sheet, Keyboard
from src.game_effect.particule import AnimatedParticule, Particule
from src.weapons.physique import *
from src.weapons.WEAPON import WEAPON

FONT = pygame.font.SysFont("Arial", 24)
INFO = pygame.display.Info()


class Action:
    def __init__(self, duration=None):
        self.duration = duration
        self.time = ...
        self.__start_time = ...
        self.__update = ...

    def update(self, *arg, **kargs):
        def func(*arg, **kargs):
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

    @property
    def next_action_type(self):
        if len(self.actions):
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

    def update(self, *args, **kwargs):
        if self.__current_action is None:
            self.__current_action = self.actions.pop(0)
        try:
            self.__current_action.update(*args, **kwargs)
        except EndAction:
            self.__current_action.clean(*args, **kwargs)
            self.__current_action = None
        for action in self.async_actions:
            try:
                action.update(*args, **kwargs)
            except EndAction:
                action.clean(*args, **kwargs)
                self.async_actions.remove(action)

    def next(self, GAME, CAMERA, _type=None):
        if self.__current_action and (not _type or type(self.__current_action) == _type):
            self.__current_action.clean(GAME, CAMERA)
            self.__current_action = None


class Turn(Action):
    def __init__(self, player, duration=None):
        super().__init__(duration)
        self.player = player

    def __update__(self, GAME, CAMERA):
        GM = GAME.partie
        GM.mobs.update(GAME, CAMERA)

        # render
        CAMERA._screen_UI.fill((0, 0, 0, 0))
        timer = self.time // 1000 + 1
        CAMERA._screen_UI.blit(FONT.render(
            str(timer), 1, (0, 0, 0)), (640, 50))

        # todo à virer après
        for player in GM.mobs.sprites():
            if type(player) == Player:
                if not player.lock:
                    CAMERA._screen_UI.blit(FONT.render(str(int(player.life_multiplicator * 100)) + "%", 1, (255, 0, 0)), (50, 50))

        CAMERA.cache = False

    def setup(self, GAME, CAMERA):
        GM = GAME.partie
        self.player.visible = True
        self.player.weapon_manager.visible = True
        self.player.weapon_manager.reload()
        for player in GM.players:
            player.lock = player != self.player

    def clean(self, GAME, CAMERA):
        GM = GAME.partie
        self.player.lock = True
        self.player.weapon_manager.visible = False
        GM.cycle_players += 1
        GM.timeline.add_action(Turn(GM.actual_player, duration=GM.cooldown_tour))


class Respawn(Action):
    def __init__(self, player, duration=5000):
        super().__init__(duration)
        self.player: Player = player
        self.interract_up = False

    def setup(self, GAME, CAMERA):
        GM = GAME.partie
        self.player.rect.topleft = GM.checkpoint()
        self.player.visible = True
        self.player.respawn()

    def __update__(self, GAME, CAMERA):
        GM = GAME.partie
        self.player.visible = True

        self.player.x_axis.update(Keyboard.right.is_pressed, Keyboard.left.is_pressed)
        if self.player.x_axis.value > 0:
            self.player.right_direction = True
        elif self.player.x_axis.value < 0:
            self.player.right_direction = False
        self.player.rect.x += self.player.x_axis * 1 * GAME.serialized * 10
        self.player.rect.x = min(max(self.player.rect.x, 100), GM.map.rect.width - self.player.rect.width - 100)

        for mob in GM.mobs.sprites():
            mob.update(GAME, CAMERA)

        #self.player.weapon_manager.update(self.player, GAME, CAMERA)
        # * CAMERA Update of the player
        x, y = CAMERA.to_virtual(INFO.current_w / 2, INFO.current_h / 2)
        _x, _y = (self.player.rect.left, self.player.rect.top)
        CAMERA.x += (_x - x) * 0.0001
        CAMERA.y += (_y - y) * 0.0001

        if Keyboard.interact.is_pressed:
            if self.interract_up:
                raise EndAction()
        else:
            self.interract_up = True

    def clean(self, GAME, CAMERA):
        GM = GAME.partie
        self.player.phatom = False
        self.player.life -= 1


class transition(Action):
    def __init__(self, duration=None):
        super().__init__(duration)


class Death(Action):
    def __init__(self, player, duration=1000):
        super().__init__(duration)
        self.player: Player = player

    def setup(self, GAME, CAMERA):
        self.player.visible = False

    def __update__(self, GAME, CAMERA):
        GM = GAME.partie
        if pygame.time.get_ticks() % 50 == 0:
            GM.group_particle.add(Particule(40, Vector2(self.player.rect.centerx, self.player.rect.bottom), 2, Vector2(0, -1), 0.5, Color(0, 0, 0), False))


class DeathTransition(Action):
    def __init__(self, duration=1000):
        super().__init__(duration)

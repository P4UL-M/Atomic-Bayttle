from __future__ import annotations
import src.weapons.WEAPON as wp
from src.tools.tools import Keyboard, ScreenSize, MixeurAudio, Vector2, Axis
from src.tools.constant import CHARGING, PATH
import pygame
from random import choice
from math import pi
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game import *
    from src.mobs.player import Player


class inventory:
    def __init__(self, team) -> None:
        self.weapon_list: list[wp.WEAPON] = [weapon(team) for weapon in wp._list_weapon]
        self.current_weapon: wp.WEAPON = choice(self.weapon_list)
        self.visible = False

        self.cooldown = 200
        self.__cooldown = 0

        self.index = self.weapon_list.index(self.current_weapon)
        self.zoom_factor = 1

        self.angle = 0
        self.x_axis = Axis()
        self.y_axis = Axis()

    def handle(self, event, owner, GAME: Game, CAMERA: Camera):
        self.current_weapon.handle(event, owner, GAME, CAMERA)

    def update(self, owner: Player, GAME: Game, CAMERA: Camera):
        """
        :param GAME: the Game constant
        :type GAME: Game
        """
        if Keyboard.interact.is_pressed and not owner.lock and not self.current_weapon.lock and not owner.input_lock:
            pygame.event.post(pygame.event.Event(CHARGING, {"weapon": self.current_weapon, "value": 0.1}))
        if Keyboard.inventory.is_pressed and not owner.lock and not self.current_weapon.lock and (not type(self.current_weapon) is wp.Auto or self.current_weapon.magazine == self.current_weapon.magazine_max) and (not type(self.current_weapon) is wp.Chainsaw or self.current_weapon.magazine > self.current_weapon.magazine_max // 2):
            _vect = Vector2(self.x_axis.value, self.y_axis.value)
            if _vect.arg is not None:
                if self.__cooldown + self.cooldown < pygame.time.get_ticks():
                    self.__cooldown = pygame.time.get_ticks()
                    if _vect.arg >= 0 and _vect.arg < pi * 1 / 4:
                        self.index = 2
                    elif _vect.arg > pi * 3 / 4 and _vect.arg <= pi:
                        self.index = 0
                    elif _vect.arg >= pi * 1 / 4 and _vect.arg <= pi * 3 / 4:
                        self.index = 1
                    self.current_weapon.clean()
                    self.current_weapon = self.weapon_list[self.index]
        if Keyboard.inventory.is_pressed and not owner.lock:
            self.y_axis.update(Keyboard.up.is_pressed, Keyboard.down.is_pressed)
            self.x_axis.update(Keyboard.right.is_pressed, Keyboard.left.is_pressed)
            if not self.current_weapon.lock and (not type(self.current_weapon) is wp.Auto or self.current_weapon.magazine == self.current_weapon.magazine_max) and (not type(self.current_weapon) is wp.Chainsaw or self.current_weapon.magazine > self.current_weapon.magazine_max // 2):
                _x, _y = CAMERA.to_absolute(owner.rect.centerx, owner.rect.centery)
                _x = _x / ScreenSize.resolution.x * CAMERA._screen_UI.get_width()
                _y = _y / ScreenSize.resolution.y * CAMERA._screen_UI.get_height()
                i = CAMERA._screen_UI.get_height() * 0.1
                j = i // 2
                tab = [(-20, -20), (0, -35), (20, -20)]
                for i, weapon in enumerate(self.weapon_list):
                    img = weapon.icon.copy()
                    img.set_alpha(255 * (1 if weapon is self.current_weapon else 0.35))
                    CAMERA._screen_UI.blit(img, (_x - img.get_width() / 2 + tab[i][0], _y - img.get_height() / 2 + tab[i][1]))
            else:
                MixeurAudio.play_effect(PATH / "assets" / "sound" / "error.wav")

        self.angle += owner.y_axis * 0.05 * GAME.serialized
        if self.angle > pi / 2:
            self.angle = pi / 2
        elif self.angle < -pi / 2:
            self.angle = -pi / 2

        self.current_weapon.update(owner.rect.center, owner.right_direction, self.angle, owner.lock, CAMERA)
        self.current_weapon.visible = self.visible and owner.visible

    def reload(self):
        for weapon in self.weapon_list:
            weapon.reload()

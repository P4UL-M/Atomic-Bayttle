from __future__ import annotations
import src.weapons.WEAPON as wp
from src.tools.tools import Keyboard, ScreenSize, MixeurAudio
from src.tools.constant import CHARGING, PATH
import pygame
from random import choice
from math import cos, sin, pi
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game import *
    from src.mobs.player import Player


class inventory:
    def __init__(self, team) -> None:
        self.weapon_list: list[wp.WEAPON] = [weapon(team) for weapon in wp._list_weapon]
        self.current_weapon: wp.WEAPON = choice(self.weapon_list)
        self.visible = False

        self.cooldown = 400
        self.__cooldown = 0

        self.index = self.weapon_list.index(self.current_weapon)
        self.zoom_factor = 1

        self.angle = 0

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
            if self.__cooldown + self.cooldown < pygame.time.get_ticks():
                self.__cooldown = pygame.time.get_ticks()
                self.index += 1
                if self.index >= len(self.weapon_list):
                    self.index = 0
                self.current_weapon.clean()
                self.current_weapon = self.weapon_list[self.index]
        if Keyboard.inventory.is_pressed and not owner.lock:
            if not self.current_weapon.lock and (not type(self.current_weapon) is wp.Auto or self.current_weapon.magazine == self.current_weapon.magazine_max) and (not type(self.current_weapon) is wp.Chainsaw or self.current_weapon.magazine > self.current_weapon.magazine_max // 2):
                _x, _y = CAMERA.to_absolute(owner.rect.centerx, owner.rect.centery)
                _x = _x / ScreenSize.resolution.x * CAMERA._screen_UI.get_width()
                _y = _y / ScreenSize.resolution.y * CAMERA._screen_UI.get_height()
                i = CAMERA._screen_UI.get_height() * 0.1
                j = i // 2
                pygame.draw.circle(CAMERA._screen_UI, (175, 175, 225, 150), (_x, _y), i)
                for _i, weapon in enumerate(self.weapon_list):
                    img = weapon.real_image.copy()
                    img.set_alpha(255 * (0.9 if weapon is self.current_weapon else 0.45))
                    CAMERA._screen_UI.blit(img, (_x + cos(_i * 2 * pi / len(self.weapon_list)) * j - weapon.real_image.get_width() // 2, _y + sin(_i * 2 * pi / len(self.weapon_list)) * j - weapon.real_image.get_height() // 2))
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

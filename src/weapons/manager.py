from __future__ import annotations
import src.weapons.WEAPON as wp
from src.tools.tools import Keyboard
from src.tools.constant import CHARGING
import pygame
from random import choice
from typing import TYPE_CHECKING
import time

if TYPE_CHECKING:
    from src.game import *


class inventory:
    def __init__(self) -> None:
        self.weapon_list = [weapon() for weapon in wp._list_weapon]
        self.current_weapon: wp.WEAPON = choice(self.weapon_list)
        self.visible = False

        self.cooldown = 200
        self.__cooldown = 0

        self.index = self.weapon_list.index(self.current_weapon)
        self.zoom_factor = 1

        self.last_switch=0

    def handle(self, event, owner, GAME: Game, CAMERA: Camera):
        self.current_weapon.handle(event, owner, GAME, CAMERA)

    def update(self, owner, GAME: Game, CAMERA: Camera):
        """
        :param GAME: the Game constant
        :type GAME: Game
        """
        if Keyboard.interact.is_pressed and not owner.lock and not self.current_weapon.lock and not owner.input_lock:
            pygame.event.post(pygame.event.Event(CHARGING, {"weapon": self.current_weapon, "value": 0.1}))
        if Keyboard.inventory.is_pressed and not owner.lock and not self.current_weapon.lock and (not type(self.current_weapon) is wp.Sniper or self.current_weapon.magazine == self.current_weapon.magazine_max) and (not type(self.current_weapon) is wp.Chainsaw or self.current_weapon.magazine > self.current_weapon.magazine_max // 2):
            if self.__cooldown + self.cooldown < pygame.time.get_ticks():
                self.__cooldown = pygame.time.get_ticks()
                self.index += 1
                if self.index >= len(self.weapon_list):
                    self.index = 0
                self.current_weapon.clean()
                self.current_weapon = self.weapon_list[self.index]
                self.last_switch=time.time()
        self.current_weapon.update(owner.rect.center, owner.right_direction, owner.y_axis * 0.05, owner.lock, CAMERA, GAME.serialized)
        self.current_weapon.visible = self.visible and owner.visible

    def reload(self):
        for weapon in self.weapon_list:
            weapon.reload()

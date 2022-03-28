import src.weapons.WEAPON as wp
from src.tools.tools import Keyboard
from src.tools.constant import CHARGING
import pygame
from random import choice


class inventory:
    def __init__(self) -> None:
        self.weapon_list = [weapon() for weapon in wp._list_weapon]
        self.current_weapon: wp.WEAPON = choice(self.weapon_list)

        self.cooldown = 200
        self.__cooldown = 0

        self.index = self.weapon_list.index(self.current_weapon)
        self.zoom_factor = 1

    def handle(self, event, owner, GAME, CAMERA):
        self.current_weapon.handle(event, owner, GAME, CAMERA)

    def update(self, owner, GAME, CAMERA):
        if Keyboard.interact.is_pressed and not owner.lock and not self.current_weapon.lock:
            pygame.event.post(pygame.event.Event(
                CHARGING, {"weapon": self.current_weapon, "value": 0.1}))
        if Keyboard.inventory.is_pressed and not owner.lock and not self.current_weapon.lock:
            if self.__cooldown + self.cooldown < pygame.time.get_ticks():
                self.__cooldown = pygame.time.get_ticks()
                self.index += 1
                if self.index >= len(self.weapon_list):
                    self.index = 0
                self.current_weapon.clean()
                self.current_weapon = self.weapon_list[self.index]
        self.current_weapon.update(
            owner.rect.center, owner.right_direction, owner.y_axis*0.05, owner.lock)

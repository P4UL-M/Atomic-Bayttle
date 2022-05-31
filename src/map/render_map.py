"""
Atomic Bay'ttle
Paul Mairesse, Axel Loones, Louis Le Meilleur, Joseph Bénard, Théo de Aranjo
This file updates the map and damage done to it
"""
import pygame
from pygame.locals import *
from src.tools.tools import Vector2, sprite_sheet, animation_Manager, MixeurAudio
from src.tools.constant import PATH
from src.weapons.WEAPON import *
import random


class Map(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(
            PATH / "assets" / "environnement" / "map.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.water_level = self.image.get_height() - 30
        self.water_target = self.image.get_height() - 30

        self.water_manager = animation_Manager()
        _water_idle = sprite_sheet(
            PATH / "assets" / "environnement" / "water_idle.png", (448, 252))
        _water_idle.config(self.rect.size)
        _water_agitated = sprite_sheet(
            PATH / "assets" / "environnement" / "water_agitated.png", (448, 252))
        _water_agitated.config(self.rect.size)
        self.water_manager.add_annimation("idle", _water_idle, 40)
        self.water_manager.add_annimation("agitated", _water_agitated, 40)
        self.water_manager.load("idle")

        self.cave_bg = pygame.sprite.Sprite()
        self.cave_bg.image = pygame.image.load(
            PATH / "assets" / "environnement" / "cave.png").convert_alpha()
        self.cave_bg.rect = self.cave_bg.image.get_rect(topleft=(927, 221))
        self.seil = 0

    def add_damage(self, _pos: Vector2, radius):  # pass damage and update mask
        # create mask from surface of deletion
        _pos = _pos - Vector2(radius, radius)
        _surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(_surf, (255, 255, 255, 255), (radius, radius), radius)
        _mask = pygame.mask.from_surface(_surf)
        # add damage to surface
        self.image.blit(_surf, _pos(), special_flags=BLEND_RGBA_SUB)
        self.cave_bg.image.blit(_surf, (_pos - self.cave_bg.rect.topleft)(), special_flags=BLEND_RGBA_SUB)
        # update mask
        self.mask.erase(_mask, _pos())
        # update water level
        if radius >= Launcher("perso_1").rayon:
            self.water_target -= 15
        else:
            self.water_target -= 1.5

    def update(self, GAME):
        MixeurAudio.gn.sound_factor.value = min(- 2 / self.rect.height * max(self.water_target, self.water_level) + 3, 3)
        if self.water_target + 1 < self.water_level:
            self.water_level -= 0.14 * GAME.serialized
            self.water_manager.load("agitated")
        elif self.water_target - 1 > self.water_level:
            self.water_level += 0.3 * GAME.serialized
            self.water_manager.load("agitated")
        else:
            self.water_manager.load("idle")

        if random.random() < self.seil:
            self.seil = 0

            def place(mask: pygame.mask.Mask):
                x = random.randint(0 + 100, self.mask.get_size()[0] - 100)
                y = 0
                while not self.mask.overlap(mask, (x, y)) and y < self.mask.get_size()[1] - 10:
                    y += 1
                if y >= self.mask.get_size()[1] - 10:
                    place(mask)
                return x, y
            img = pygame.image.load(PATH / "assets" / "weapons" / "shield.png")
            x, y = place(pygame.mask.from_surface(img))
            y -= 10
            GAME.partie.add_object("heal", (x, y), PATH / "assets" / "weapons" / "shield.png")
        else:
            self.seil += 0.0000011112 * GAME.serialized

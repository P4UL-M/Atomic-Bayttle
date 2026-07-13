"""
Atomic Bay'ttle
Paul Mairesse, Axel Loones, Louis Le Meilleur, Joseph Bénard, Théo de Aranjo
This file updates the map and damage done to it
"""
import pygame
from src.tools.tools import Vector2, sprite_sheet, animation_Manager, MixeurAudio
from src.tools.constant import PATH
from src.rendering import DamageStamp
import random


class Map(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(PATH / "assets" / "environnement" / "map.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.water_level = self.image.get_height() - 30
        self.water_target = self.image.get_height() - 30

        self.water_manager = animation_Manager()
        _water_idle = sprite_sheet(
            PATH / "assets" / "environnement" / "water_idle.png", (448, 252))
        _water_agitated = sprite_sheet(
            PATH / "assets" / "environnement" / "water_agitated.png", (448, 252))
        self.water_manager.add_annimation("idle", _water_idle, 40)
        self.water_manager.add_annimation("agitated", _water_agitated, 40)
        self.water_manager.load("idle")

        self.cave_bg = pygame.sprite.Sprite()
        self.cave_bg.image = pygame.image.load(PATH / "assets" / "environnement" / "cave.png").convert_alpha()
        self.cave_bg.rect = self.cave_bg.image.get_rect(topleft=(927, 221))
        self.cave_bg.mask = pygame.mask.from_surface(self.cave_bg.image)
        self.shield_image = pygame.image.load(
            PATH / "assets" / "weapons" / "shield.png"
        ).convert_alpha()
        self.shield_mask = pygame.mask.from_surface(self.shield_image)
        self.seil = 0

    def apply_damage(self, center: Vector2, stamp: DamageStamp, renderer, radius=0):
        """Erase an arbitrary alpha stamp and upload only intersecting pixels."""
        world_bounds = stamp.bounds_at(center)
        map_bounds = world_bounds.clip(self.rect)
        if map_bounds.width and map_bounds.height:
            source = pygame.Rect(
                map_bounds.x - world_bounds.x,
                map_bounds.y - world_bounds.y,
                map_bounds.width,
                map_bounds.height,
            )
            self.image.blit(
                stamp.surface, map_bounds.topleft, source,
                special_flags=pygame.BLEND_RGBA_SUB,
            )
            self.mask.erase(stamp.mask, world_bounds.topleft)
            renderer.update_region(self.image, map_bounds)

        cave_world = world_bounds.clip(self.cave_bg.rect)
        if cave_world.width and cave_world.height:
            source = pygame.Rect(
                cave_world.x - world_bounds.x,
                cave_world.y - world_bounds.y,
                cave_world.width,
                cave_world.height,
            )
            cave_local = cave_world.move(-self.cave_bg.rect.x, -self.cave_bg.rect.y)
            self.cave_bg.image.blit(
                stamp.surface, cave_local.topleft, source,
                special_flags=pygame.BLEND_RGBA_SUB,
            )
            self.cave_bg.mask.erase(stamp.mask, (
                world_bounds.x - self.cave_bg.rect.x,
                world_bounds.y - self.cave_bg.rect.y,
            ))
            renderer.update_region(self.cave_bg.image, cave_local)

        # update water level
        if radius >= 50:
            self.water_target -= 15
        else:
            self.water_target -= 1.5

    def add_damage(self, position: Vector2, radius, renderer=None):
        """Compatibility helper for circular impacts."""
        stamp = DamageStamp.circle(round(radius))
        if renderer is None:
            raise ValueError("renderer is required for terrain texture updates")
        self.apply_damage(position, stamp, renderer, radius)

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
            x, y = place(self.shield_mask)
            y -= 10
            GAME.partie.add_object("heal", (x, y), PATH / "assets" / "weapons" / "shield.png")
        else:
            self.seil += 0.0000011112 * GAME.serialized

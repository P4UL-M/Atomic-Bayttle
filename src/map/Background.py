"""Preloaded parallax background assets."""

import pygame

from src.tools.constant import PATH
from src.tools.tools import sprite_sheet


class BackgroundAssets:
    def __init__(self):
        self.frames = list(
            sprite_sheet(
                PATH / "assets" / "environnement" / "background_sheet.png",
                (448, 252),
            )
        )
        self.back_cloud = pygame.image.load(
            PATH / "assets" / "environnement" / "cloud_back_sheet.png"
        ).convert_alpha()
        self.front_cloud = pygame.image.load(
            PATH / "assets" / "environnement" / "cloud_front_sheet.png"
        ).convert_alpha()

    def current(self):
        frame = self.frames[pygame.time.get_ticks() // 150 % len(self.frames)]
        return frame, self.back_cloud, self.front_cloud

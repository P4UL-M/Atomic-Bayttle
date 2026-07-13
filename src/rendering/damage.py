from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import pygame


@dataclass(frozen=True)
class DamageStamp:
    """An arbitrary alpha texture used to remove destructible terrain."""

    surface: pygame.Surface
    mask: pygame.mask.Mask
    hotspot: tuple[int, int]

    @classmethod
    def from_surface(cls, surface: pygame.Surface, hotspot=None) -> "DamageStamp":
        surface = surface.convert_alpha() if pygame.display.get_surface() else surface.copy()
        hotspot = hotspot or (surface.get_width() // 2, surface.get_height() // 2)
        return cls(surface, pygame.mask.from_surface(surface), tuple(hotspot))

    @classmethod
    @lru_cache(maxsize=32)
    def circle(cls, radius: int) -> "DamageStamp":
        radius = max(1, int(radius))
        surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, "white", (radius, radius), radius)
        return cls(surface, pygame.mask.from_surface(surface), (radius, radius))

    def bounds_at(self, center) -> pygame.Rect:
        return self.surface.get_rect(
            topleft=(round(center[0] - self.hotspot[0]), round(center[1] - self.hotspot[1]))
        )

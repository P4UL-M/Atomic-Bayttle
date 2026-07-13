from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import pygame


@dataclass
class Camera2D:
    """Camera using the coordinate model of the historical renderer."""

    world_size: tuple[int, int] = (1536, 864)
    framebuffer_size: tuple[int, int] = (1536, 864)
    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0
    maximise: bool = True

    @property
    def aspect_zoom(self) -> tuple[float, float]:
        world_ratio = self.world_size[0] / self.world_size[1]
        screen_ratio = self.framebuffer_size[0] / self.framebuffer_size[1]
        if not self.maximise:
            return 1.0, 1.0
        if world_ratio > screen_ratio:
            return world_ratio / screen_ratio, 1.0
        return 1.0, screen_ratio / world_ratio

    def clamp(self) -> None:
        self.zoom = max(1.0, self.zoom)
        x_zoom, y_zoom = self.aspect_zoom
        x_limit = (self.zoom - 1) / (self.zoom * 2) + (x_zoom - 1) / (2 * self.zoom)
        y_limit = (self.zoom - 1) / (self.zoom * 2) + (y_zoom - 1) / (2 * self.zoom)
        self.x = max(-x_limit, min(x_limit, self.x))
        self.y = max(-y_limit, min(y_limit, self.y))

    def update(self, x=None, y=None, zoom=None, maximise=None) -> None:
        if x is not None:
            self.x = float(x)
        if y is not None:
            self.y = float(y)
        if zoom is not None:
            self.zoom = float(zoom)
        if maximise is not None:
            self.maximise = bool(maximise)
        self.clamp()

    def world_to_view(self, position: Sequence[float]) -> tuple[float, float]:
        self.clamp()
        x_zoom, y_zoom = self.aspect_zoom
        x = ((position[0] / self.world_size[0] - 0.5 - self.x) * self.zoom * x_zoom + 0.5)
        y = ((position[1] / self.world_size[1] - 0.5 - self.y) * self.zoom * y_zoom + 0.5)
        return x * self.world_size[0], y * self.world_size[1]

    def view_to_world(self, position: Sequence[float]) -> tuple[int, int]:
        self.clamp()
        x_zoom, y_zoom = self.aspect_zoom
        x = (position[0] / self.framebuffer_size[0] - 0.5) / (self.zoom * x_zoom) + self.x + 0.5
        y = (position[1] / self.framebuffer_size[1] - 0.5) / (self.zoom * y_zoom) + self.y + 0.5
        return int(x * self.world_size[0]), int(y * self.world_size[1])

    def world_to_window(self, position: Sequence[float]) -> tuple[int, int]:
        view_x, view_y = self.world_to_view(position)
        return (
            int(view_x / self.world_size[0] * self.framebuffer_size[0]),
            int(view_y / self.world_size[1] * self.framebuffer_size[1]),
        )

    def project_rect(self, rect: pygame.Rect) -> pygame.Rect:
        left, top = self.world_to_view(rect.topleft)
        right, bottom = self.world_to_view(rect.bottomright)
        return pygame.Rect(round(left), round(top), round(right - left), round(bottom - top))

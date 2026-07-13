from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import pygame
from pygame_easy_menu import ModernGLBackend

from .camera import Camera2D


class TextureCache:
    """Revision tracker around pygame-easy-menu's shared GL texture cache."""

    def __init__(self, backend: ModernGLBackend):
        self.backend = backend
        self._revisions: dict[int, int] = {}

    def revision(self, surface: pygame.Surface) -> int:
        return self._revisions.get(id(surface), 0)

    def update_region(self, surface: pygame.Surface, rect: pygame.Rect) -> int:
        revision = self.revision(surface) + 1
        self._revisions[id(surface)] = revision
        self.backend.update_surface_region(surface, rect, revision=revision)
        return revision

    @property
    def texture_count(self) -> int:
        return self.backend.texture_count

    def release(self) -> None:
        self._revisions.clear()


class Renderer2D:
    """Pass-based 2D renderer sharing the Pygame OpenGL context."""

    def __init__(self, context, framebuffer_size: Sequence[int]):
        self.context = context
        self.framebuffer_size = tuple(map(int, framebuffer_size))
        self.backend = ModernGLBackend.from_context(
            context, self.framebuffer_size, self.framebuffer_size
        )
        self.textures = TextureCache(self.backend)
        self._pass_active = False
        self._camera: Camera2D | None = None
        self.draw_calls = 0

    def begin_frame(self, clear_color=(0.0, 0.0, 0.0, 1.0)) -> None:
        if self._pass_active:
            self.backend.end()
        self._pass_active = False
        self.draw_calls = 0
        self.context.viewport = (0, 0, *self.framebuffer_size)
        self.context.clear(*clear_color)

    def begin_pass(self, logical_size: Sequence[int], camera: Camera2D | None = None) -> None:
        if self._pass_active:
            self.backend.end()
        self.backend.configure_view(logical_size, self.framebuffer_size)
        self.backend.begin()
        self._pass_active = True
        self._camera = camera

    def draw(
        self,
        surface: pygame.Surface,
        destination,
        *,
        source_rect=None,
        angle=0.0,
        flip_x=False,
        flip_y=False,
        tint=(1.0, 1.0, 1.0, 1.0),
        opacity=None,
        revision=None,
    ) -> None:
        rect = pygame.Rect(destination)
        if self._camera is not None:
            rect = self._camera.project_rect(rect)
        if opacity is None:
            surface_alpha = surface.get_alpha()
            opacity = 1.0 if surface_alpha is None else surface_alpha / 255
        self.backend.draw_surface(
            surface,
            rect,
            source_rect=source_rect,
            angle=angle,
            flip_x=flip_x,
            flip_y=flip_y,
            tint=tint,
            opacity=opacity,
            revision=self.textures.revision(surface) if revision is None else revision,
        )
        self.draw_calls += 1

    def draw_sprite(self, item) -> None:
        if not getattr(item, "visible", True):
            return
        self.draw(
            item.image,
            getattr(item, "render_rect", item.rect),
            source_rect=getattr(item, "source_rect", None),
            angle=getattr(item, "render_angle", 0.0),
            flip_x=getattr(item, "render_flip_x", False),
            flip_y=getattr(item, "render_flip_y", False),
            tint=getattr(item, "render_tint", (1.0, 1.0, 1.0, 1.0)),
            opacity=getattr(item, "render_opacity", None),
        )

    def draw_group(self, group) -> None:
        for item in group.sprites():
            self.draw_sprite(item)

    def push_clip(self, rect) -> None:
        clip = pygame.Rect(rect)
        if self._camera is not None:
            clip = self._camera.project_rect(clip)
        self.backend.push_clip(clip)

    def pop_clip(self) -> None:
        self.backend.pop_clip()

    def update_region(self, surface: pygame.Surface, rect) -> int:
        return self.textures.update_region(surface, pygame.Rect(rect))

    def end_frame(self) -> None:
        if self._pass_active:
            self.backend.end()
        self._pass_active = False
        self._camera = None

    def release(self) -> None:
        self.textures.release()
        self.backend.release()


@dataclass
class _QueuedDraw:
    surface: pygame.Surface
    rect: pygame.Rect
    source_rect: pygame.Rect | None = None
    opacity: float | None = None


class RenderQueueSurface:
    """Surface-like command queue used by the existing HUD producers."""

    def __init__(self, size: Sequence[int]):
        self._size = tuple(map(int, size))
        self.commands: list[_QueuedDraw] = []

    def get_size(self):
        return self._size

    def get_width(self):
        return self._size[0]

    def get_height(self):
        return self._size[1]

    def fill(self, *_args, **_kwargs):
        self.commands.clear()

    def blit(self, surface, destination, area=None, special_flags=0):
        if special_flags:
            raise ValueError("RenderQueueSurface does not support CPU blend flags")
        rect = surface.get_rect(topleft=destination)
        self.commands.append(_QueuedDraw(surface, rect, area))
        return rect

    def blit_scaled(self, surface, destination, area=None, opacity=None):
        rect = pygame.Rect(destination)
        self.commands.append(_QueuedDraw(surface, rect, area, opacity))
        return rect

    def render(self, renderer: Renderer2D):
        for command in self.commands:
            renderer.draw(
                command.surface,
                command.rect,
                source_rect=command.source_rect,
                opacity=command.opacity,
            )

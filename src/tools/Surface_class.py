from __future__ import annotations
import pygame
from typing import Tuple, List, Union, Optional
from pygame import Surface, Rect
from OpenGL.GL import *


def getTexture(pygame_surface: pygame.Surface, rgba=False):
    Text = glGenTextures(1)
    rgb_surface = pygame.image.tostring(pygame_surface, 'RGBA' if rgba else 'RGB')
    glBindTexture(GL_TEXTURE_2D, Text)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    surface_rect = pygame_surface.get_rect()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA if rgba else GL_RGB, surface_rect.width, surface_rect.height, 0, GL_RGBA if rgba else GL_RGB, GL_UNSIGNED_BYTE, rgb_surface)
    glGenerateMipmap(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, 0)
    return Text


class SurfaceOpenGl(pygame.Surface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tex = None
        self.Texs: dict = {}

    def __update__(self):
        self.tex = getTexture(self, True)

    def blit(self, *args, **kargs) -> pygame.Rect:
        if type(args[0]) is not SurfaceOpenGl:
            return super().blit(*args, **kargs)
        else:
            print("blit")
            self.Texs[args[0]] = [*args[1:], kargs]

    def clean(self):
        self.Texs = {}

    def render(self, func):
        func(self.tex)
        for surf, args in self.Texs.items():
            func(surf, args)

    def copy(self) -> Surface:
        print("copy")
        return Surface2SurfaceOpenGl(super().copy())


def Surface2SurfaceOpenGl(surface: pygame.Surface) -> SurfaceOpenGl:
    _surf = SurfaceOpenGl(surface.get_size(), pygame.SRCALPHA)
    _surf.blit(surface, (0, 0))
    return _surf

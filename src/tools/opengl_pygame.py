"""
Atomic Bay'ttle
Paul Mairesse, Axel Loones, Louis Le Meilleur, Joseph Bénard, Théo de Aranjo
This file contains functions to link OpenGL and Pygame
"""
from OpenGL.GL import *
from src.tools.tools import ScreenSize
import pygame

# basic opengl configuration


def config():
    glViewport(0, 0, ScreenSize.resolution.x, ScreenSize.resolution.y)
    glDepthRange(0, 1)
    glMatrixMode(GL_PROJECTION)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    glEnable(GL_BLEND)


texID = glGenTextures(1)
texUI = glGenTextures(1)


def surfaceToTexture(pygame_surface: pygame.Surface, text, rgba=False):
    rgb_surface = pygame.image.tostring(pygame_surface, 'RGBA' if rgba else 'RGB')
    glBindTexture(GL_TEXTURE_2D, text)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    surface_rect = pygame_surface.get_rect()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA if rgba else GL_RGB, surface_rect.width, surface_rect.height, 0, GL_RGBA if rgba else GL_RGB, GL_UNSIGNED_BYTE, rgb_surface)
    glGenerateMipmap(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, 0)


def returnSurfaceToTexture(pygame_surface: pygame.Surface, rgba=False):
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


def surfaceToScreen(pygame_surface: pygame.Surface, pos: tuple[float, float], zoom: float, maximize=True) -> tuple[float, float, tuple[float, float]]:
    x, y = pos
    surf_ratio = pygame_surface.get_width() / pygame_surface.get_height()  # 10/5 -> 2
    screen_ratio = ScreenSize.resolution.x / ScreenSize.resolution.y  # 9/5 -> 1.8
    if maximize:
        if surf_ratio > screen_ratio:
            y_zoom = 1
            x_zoom = surf_ratio / screen_ratio
        else:
            x_zoom = 1
            y_zoom = screen_ratio / surf_ratio
    else:
        y_zoom = 1
        x_zoom = 1

    x = max(min((zoom - 1) / (zoom * 2) + (x_zoom - 1) / 2 / zoom, x), -(zoom - 1) / (zoom * 2) - (x_zoom - 1) / 2 / zoom)
    y = max(min((zoom - 1) / (zoom * 2) + (y_zoom - 1) / 2 / zoom, y), -(zoom - 1) / (zoom * 2) - (y_zoom - 1) / 2 / zoom)

    # draw texture openGL Texture
    surfaceToTexture(pygame_surface, texID, True)

    glBindTexture(GL_TEXTURE_2D, texID)
    glBegin(GL_QUADS)
    glTexCoord2f(x, y)
    glVertex2f(-zoom * x_zoom, zoom * y_zoom)
    glTexCoord2f(x, y + 1)
    glVertex2f(-zoom * x_zoom, -zoom * y_zoom)
    glTexCoord2f(x + 1, y + 1)
    glVertex2f(zoom * x_zoom, -zoom * y_zoom)
    glTexCoord2f(x + 1, y)
    glVertex2f(zoom * x_zoom, zoom * y_zoom)
    glEnd()

    return x, y, (x_zoom, y_zoom)


def checkCoord(x, y, zoom, surface, maximize=True):
    surf_ratio = surface.get_width() / surface.get_height()  # 10/5 -> 2
    screen_ratio = ScreenSize.resolution.x / ScreenSize.resolution.y  # 9/5 -> 1.8
    if maximize:
        if surf_ratio > screen_ratio:
            y_zoom = 1
            x_zoom = surf_ratio / screen_ratio
        else:
            x_zoom = 1
            y_zoom = screen_ratio / surf_ratio
    else:
        y_zoom = 1
        x_zoom = 1

    zoom = max(zoom, 1)
    x = max(min((zoom - 1) / (zoom * 2) + (x_zoom - 1) / 2 / zoom, x), -(zoom - 1) / (zoom * 2) - (x_zoom - 1) / 2 / zoom)
    y = max(min((zoom - 1) / (zoom * 2) + (y_zoom - 1) / 2 / zoom, y), -(zoom - 1) / (zoom * 2) - (y_zoom - 1) / 2 / zoom)
    return x, y, zoom


def uiToScreen(pygame_surface: pygame.Surface):
    if pygame_surface:
        surfaceToTexture(pygame_surface, texUI, True)

    glBindTexture(GL_TEXTURE_2D, texUI)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(-1, 1)
    glTexCoord2f(0, 1)
    glVertex2f(-1, -1)
    glTexCoord2f(1, 1)
    glVertex2f(1, -1)
    glTexCoord2f(1, 0)
    glVertex2f(1, 1)
    glEnd()


def simpleRender(text, pos: tuple[float, float], size, zoom: float, maximize=True, offset=(0, 0)):
    x, y = pos

    surf_ratio = size[0] / size[1]  # 10/5 -> 2
    screen_ratio = ScreenSize.resolution.x / ScreenSize.resolution.y  # 9/5 -> 1.8
    if maximize:
        if surf_ratio > screen_ratio:
            y_zoom = 1
            x_zoom = surf_ratio / screen_ratio
        else:
            x_zoom = 1
            y_zoom = screen_ratio / surf_ratio
    else:
        y_zoom = 1
        x_zoom = 1

    x = max(min((zoom - 1) / (zoom * 2) + (x_zoom - 1) / 2 / zoom, x), -(zoom - 1) / (zoom * 2) - (x_zoom - 1) / 2 / zoom)
    y = max(min((zoom - 1) / (zoom * 2) + (y_zoom - 1) / 2 / zoom, y), -(zoom - 1) / (zoom * 2) - (y_zoom - 1) / 2 / zoom)

    glBindTexture(GL_TEXTURE_2D, text)
    glBegin(GL_QUADS)
    glTexCoord2f(x, y)
    glVertex2f(-zoom * x_zoom + offset[0], zoom * y_zoom + offset[1])
    glTexCoord2f(x, y + 1)
    glVertex2f(-zoom * x_zoom + offset[0], -zoom * y_zoom + offset[1])
    glTexCoord2f(x + 1, y + 1)
    glVertex2f(zoom * x_zoom + offset[0], -zoom * y_zoom + offset[1])
    glTexCoord2f(x + 1, y)
    glVertex2f(zoom * x_zoom + offset[0], zoom * y_zoom + offset[1])
    glEnd()

    return x, y, (x_zoom, y_zoom)


def cleangl():
    # prepare to render the texture-mapped rectangle
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glDisable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(0, 0, 0, 1.0)

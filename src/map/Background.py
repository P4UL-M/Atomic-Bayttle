"""
Atomic Bay'ttle
Paul Mairesse, Axel Loones, Louis Le Meilleur, Joseph Bénard, Théo de Aranjo
This file allow to render the background of the game with opengl
"""
import pygame
from pygame.locals import *
import src.tools.opengl_pygame as gl
from src.tools.tools import sprite_sheet
from src.tools.constant import PATH


def background():
    sp = sprite_sheet(PATH / "assets" / "environnement" / "background_sheet.png", (448, 252))
    _bgs = [gl.returnSurfaceToTexture(spr) for spr in sp]

    _b_cloud = gl.returnSurfaceToTexture(pygame.image.load(PATH / "assets" / "environnement" / "cloud_back_sheet.png"), True)
    _f_cloud = gl.returnSurfaceToTexture(pygame.image.load(PATH / "assets" / "environnement" / "cloud_front_sheet.png"), True)

    while True:
        yield _bgs[pygame.time.get_ticks() // 150 % len(_bgs)], (448, 252), _b_cloud, pygame.time.get_ticks() / 40000 % 0.5 - 0.25, (896, 252), _f_cloud, pygame.time.get_ticks() / 80000 % 0.5 - 0.25, (896, 252)

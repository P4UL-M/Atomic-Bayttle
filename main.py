from tools.generate_music import p,set_path
import pathlib
import pygame_edit
import pygame
from pygame.locals import *

PATH = pathlib.Path(__file__).parent

set_path(PATH / "assets" / "music" / "Halloween LOOP.wav")

INFO = pygame.display.Info()


if __name__=="__main__":
    p.start()
    
    pygame.init()
    pygame.display.set_mode((INFO.current_w,INFO.current_h), OPENGL|DOUBLEBUF|FULLSCREEN)
    pygame.display.init()

    import tools.opengl_pygame as gl

    from game import Game as game

    try:
        game.run(gl)
    except SystemExit:
        p.kill()
        print("bye !")
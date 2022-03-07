import pygame
from pygame.locals import *

pygame.init()
INFO = pygame.display.Info()

pygame.display.set_mode((INFO.current_w,INFO.current_h), OPENGL|DOUBLEBUF|FULLSCREEN,depth=16)
pygame.display.init()

import pathlib
import tools.opengl_pygame as gl
from tools.tools import MixeurAudio
import menu_main
#import test
import game_manager

PATH = pathlib.Path(__file__).parent
INFO = pygame.display.Info()

# there is only one game so we do not need a instance, modifying dinamically the class allow us to access it without an instance
class Game:
    running = True
    clock = pygame.time.Clock()
    serialized = 0

    def run():
        MixeurAudio.set_musique(path=PATH / "assets" / "music" / "main-loop.wav")
        MixeurAudio.play_until_Stop(PATH / "assets" / "sound" / "water_effect_loop.wav",volume=0.35)
        gl.config(INFO)
        partie = game_manager.Partie()
        partie.add_player("j1","perso_4")
        partie.camera_target = partie.mobs.sprites()[0]
        Camera.zoom = 3

        while Game.running:
            partie.Update()

            Camera.render()
            print(Game.clock.get_fps())
            pygame.display.flip()

            Game.serialized = Game.clock.tick(60)/16.7
        else:
            raise SystemExit

class Camera:
    x = 0
    y = 0
    zoom = 1
    zoom_offset = (1,1)
    maximise = True
    HUD = False
    _off_screen:pygame.Surface = pygame.Surface((1280,720))
    _screen_UI:pygame.Surface = pygame.Surface((1280,720),flags=SRCALPHA)

    def render() -> None:
        gl.cleangl()
        Camera.zoom = max(1,Camera.zoom)
        Camera.x,Camera.y,Camera.zoom_offset = gl.surfaceToScreen(Camera._off_screen,(Camera.x,Camera.y),Camera.zoom,maximize=Camera.maximise)
        # add when we will need UI, for now render is not fully optimised so we wont render useless surface
        if Camera.HUD:
            gl.surfaceToScreen(Camera._screen_UI,(0,0),1,True) # try to blit only if not null take more time to check than blit it anyway
    
    def to_virtual(x,y) -> tuple[int,int]:

        x_zoom = Camera.zoom*Camera.zoom_offset[0]
        local = x/INFO.current_w - 0.5
        _x = local/x_zoom + Camera.x + 0.5

        y_zoom = Camera.zoom*Camera.zoom_offset[1]
        local = y/INFO.current_h - 0.5
        _y = local/y_zoom + Camera.y + 0.5

        return (int(_x*Camera._off_screen.get_width()), int(_y*Camera._off_screen.get_height()))

    def to_absolute(x,y) -> tuple[int,int]:

        x_zoom = Camera.zoom*Camera.zoom_offset[0]
        _x = (x/Camera._off_screen.get_width() -0.5 - Camera.x) * x_zoom + 0.5

        y_zoom = Camera.zoom*Camera.zoom_offset[1]
        _y = (y/Camera._off_screen.get_height() -0.5 - Camera.y) * y_zoom + 0.5

        return (int(_x * INFO.current_w),int(_y * INFO.current_h))

# class parent now accessible to childs too
game_manager.GAME = menu_main.GAME= Game
game_manager.CAMERA = menu_main.CAMERA = Camera
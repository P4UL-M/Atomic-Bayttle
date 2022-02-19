import pygame
from pygame.locals import *

import pathlib

from tools.tools import MixeurAudio,Vector2
import game_manager
import menu_main
import test

PATH = pathlib.Path(__file__).parent
INFO = pygame.display.Info()

# there is only one game so we do not need a instance, modifying dinamically the class allow us to access it without an instance
class Game:
    running = True
    clock = pygame.time.Clock()
    serialized = 0

    def run(gl):
        MixeurAudio.set_musique(path=PATH / "assets" / "music" / "main-loop.wav")
        MixeurAudio.play_until_Stop(PATH / "assets" / "sound" / "water_effect_loop.wav",volume=0.35)
        gl.config(INFO)
        
        while Game.running:
            Game.serialized = 16.7/(Game.clock.tick() or 16.7)
            # boucle to intercept only the quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Game.running = False
                else:
                    pygame.event.post(event)
            
            Camera.render(gl)
            test.loop(PATH)
            print(pygame.mouse.get_pos())
            pygame.display.flip()
        else:
            raise SystemExit

class Camera:
    x = 0
    y = 0
    zoom = 1
    _off_screen:pygame.Surface = pygame.Surface((1600,900),flags=HWSURFACE + HWACCEL)
    _screen_UI:pygame.Surface = pygame.Surface((INFO.current_w,INFO.current_h),flags=SRCALPHA + HWSURFACE + HWACCEL)

    def render(gl) -> None:
        gl.cleangl()
        Camera.x,Camera.y = gl.surfaceToScreen(Camera._off_screen,(Camera.x,Camera.y),Camera.zoom)
        gl.surfaceToScreen(Camera._screen_UI,(0,0),1)
    
    def to_virtual(x,y) -> tuple[int,int]:
        _x = x/INFO.current_w +Camera.x/Camera.zoom
        _y = y/INFO.current_h +Camera.y/Camera.zoom
        return (int(Camera._off_screen.get_width() * _x), int(Camera._off_screen.get_height()*_y))

    def to_absolute(x,y) -> tuple[int,int]:
        _x = x/Camera._off_screen.get_width() - Camera.x/Camera.zoom
        _y = y/_x, Camera._off_screen.get_height() - Camera.y/Camera.zoom
        return (int(_x * INFO.current_w),int(_y * INFO.current_h))

# class parent now accessible to childs too
game_manager.GAME = menu_main.GAME = Game
game_manager.CAMERA = menu_main.CAMERA = Camera

import pygame
pygame.init()
import game_manager
import menu_main
from tools.tools import Keyboard, MixeurAudio
import pathlib


PATH = pathlib.Path(__file__).parent

# there is only one game so we do not need a instance, modifying dinamically the class allow us to access it without an instance
class Game: 
    size = (pygame.display.Info().current_w,pygame.display.Info().current_h)
    running = True
    clock = pygame.time.Clock()
    serialized = 0

    def run():
        pygame.display.set_mode(Game.size,pygame.RESIZABLE)
        MixeurAudio.set_musique(path=PATH / "assets" / "music" / "main-loop.wav")
        MixeurAudio.play_until_Stop(PATH / "assets" / "sound" / "water_effect_loop.wav",volume=0.35)
        while Game.running:
            Game.serialized = 16.7/(Game.clock.tick() or 16.7)
            # boucle to intercept only the quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Game.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    MixeurAudio.play_effect(PATH / "assets" / "sound" / "button-menu.wav")
                else:
                    pygame.event.post(event)
                        

            pygame.display.update()
        else:
            raise SystemExit

# class parent now accessible to childs too
game_manager.GAME = menu_main.GAME = Game

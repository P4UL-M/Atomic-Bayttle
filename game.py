import pygame
import screeninfo
import game_main
import menu_main

pygame.init()

class Game:
    size = (screeninfo.screeninfo.get_monitors()[0].width,screeninfo.screeninfo.get_monitors()[0].height)
    running = True

    def run():
        pygame.display.set_mode(Game.size,pygame.RESIZABLE)
        while Game.running:
            # boucle to intercept only the quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Game.running = False
                else:
                    pygame.event.post(event)
            pygame.display.update()
        else:
            raise SystemExit
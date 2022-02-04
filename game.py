import pygame
import screeninfo

pygame.init()

class Game:
    size = (screeninfo.screeninfo.get_monitors()[0].width,screeninfo.screeninfo.get_monitors()[0].height)
    running = True

    def run():
        pygame.display.set_mode(Game.size,pygame.RESIZABLE)
        while Game.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Game.running = False
            pygame.display.update()
        else:
            raise SystemExit
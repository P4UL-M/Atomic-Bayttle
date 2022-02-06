import pygame
import screeninfo
import game_main
import menu_main

pygame.init()

class Game:
    size = (pygame.display.Info().current_w,pygame.display.Info().current_h)
    running = True
    clock = pygame.time.Clock()
    serialized = 0

    def run():
        pygame.display.set_mode(Game.size,pygame.RESIZABLE)
        while Game.running:
            Game.serialized = 16.7/Game.clock.tick(60)
            # boucle to intercept only the quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Game.running = False
                else:
                    pygame.event.post(event)
            pygame.display.update()
        else:
            raise SystemExit
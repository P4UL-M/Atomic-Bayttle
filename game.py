import pygame
import game_manager
import menu_main

pygame.init()

# there is only one game so we do not need a instance, modifying dinamically the class allow us to access it without an instance
class Game: 
    size = (pygame.display.Info().current_w,pygame.display.Info().current_h)
    running = True
    clock = pygame.time.Clock()
    serialized = 0

    def run():
        pygame.display.set_mode(Game.size,pygame.RESIZABLE)
        while Game.running:
            Game.serialized = 16.7/(Game.clock.tick() or 16.7)
            # boucle to intercept only the quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Game.running = False
                else:
                    pygame.event.post(event)
                      
            pygame.display.update()
        else:
            raise SystemExit

# class parent now accessible to childs too
game_manager.GAME = menu_main.GAME = Game

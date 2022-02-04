import os
from game import Game
import pygame

pygame.init()

if __name__ == "__main__":

    game = Game()
    game.run()
    
    # https://stackoverflow.com/questions/62058750/how-to-check-collisions-between-a-mask-and-rect-in-pygame
    # https://www.pygame.org/docs/ref/mask.html
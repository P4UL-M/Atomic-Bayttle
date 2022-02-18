import pygame 
from tools.tools import annimation_Manager
from typing import Union

# rewrite of get_pos to send now the pos in the virtual surface and not the screen.
def get_pos(func):
    def wrap(abs=False):
        if abs:
            return func()
        else:
            coord = func()
            return (coord[0],coord[0])
    
    return wrap

pygame.mouse.get_pos = get_pos(pygame.mouse.get_pos)
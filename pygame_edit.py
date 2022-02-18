import pygame 
from tools.tools import animation_Manager
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

# rewite directly the class because we can't setattr on C based class
# allow us to pass a animation_Manager to blit
class mySurf(pygame.surface.Surface):

    def blit(self,source:Union[pygame.Surface,animation_Manager],dest,*arg,**kargs) -> pygame.Rect:
        if type(self)==pygame.Surface:
            return super().blit(source,dest,*arg,**kargs)
        elif type(self)==animation_Manager:
            return super().blit(source.surface,dest,*arg,**kargs)

pygame.Surface = mySurf
pygame.surface.Surface = mySurf
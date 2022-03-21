import pygame
from src.tools.constant import EndAction

class Action:
    def __init__(self):
        self.type = ...
        self.duration = ...
        self.time = ...
        self.__start_time = pygame.time.get_ticks()
        self.__update = ...

    def update(self):
        self.time = self.duration - (pygame.time.get_ticks() - self.__start_time)
        if self.time >= 0:
            raise EndAction
        elif self.__update:
            self.__update()
        
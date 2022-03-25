import pygame
from src.tools.constant import EndAction

class Action:
    def __init__(self, duration=None):
        self.duration = duration
        self.time = ...
        self.__start_time = pygame.time.get_ticks()
        self.__update = ...

    def update(self):
        if self.duration is not None:
            self.time = self.duration - (pygame.time.get_ticks() - self.__start_time)
        else:
            self.time = 1
        if self.time <= 0:
            raise EndAction
        elif self.__update:
            self.__update()

    def set_update(self, update):
        self.__update = update

class timeline:
    def __init__(self):
        self.actions = []
        self.__current_action = None
    
    def add_action(self, action):
        self.actions.append(action)
        if not self.current_action:
            self.current_action = self.actions.pop(0)
    
    def update(self):
        if self.__current_action is None:
            self.__current_action = self.actions.pop(0)
        try:
            self.__current_action.update()
        except EndAction:
            self.__current_action = None
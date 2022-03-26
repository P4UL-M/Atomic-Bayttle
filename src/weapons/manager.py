import src.weapons.WEAPON as wp
from src.tools.tools import Keyboard
from src.tools.constant import CHARGING
import pygame
from random import choice


class inventory:
    def __init__(self) -> None:
        self.weapon_list = wp._list_weapon
        self.current_weapon:wp.WEAPON = choice(self.weapon_list)()

    def handle(self,event,owner,GAME,CAMERA):
        self.current_weapon.handle(event,owner,GAME,CAMERA)
        #self.current_weapon.fire(self.right_direction,GM.mobs,GM.group_particle)
    
    def update(self,owner,GAME,CAMERA):
        if Keyboard.interact.is_pressed and not owner.lock and not self.current_weapon.lock:
            pygame.event.post(pygame.event.Event(CHARGING,{"weapon":self.current_weapon,"value":0.1}))
        self.current_weapon.update(owner.rect.center,owner.right_direction,owner.y_axis*0.05,owner.lock)
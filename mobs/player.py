import pygame
from .MOTHER import MOB
import pathlib
from tools.tools import animation_Manager, sprite_sheet,Keyboard

PATH = pathlib.Path(__file__).parent
INFO = pygame.display.Info()

class Player(MOB):

    def __init__(self,name, pos, size,team,group):
        """parametres :
            - pos : les position de base
            - size : la taille du sprite
            - team : la team d'image à charger
            - group : le group de sprite a ajouter le sprite
        """
        # initialisation de la classe mere permettant de faire de cette classe un sprite
        super().__init__(pos,size,group)
        self.name = name

        self.image = pygame.Surface(size)
        self.image.fill((255,0,0)) #! tempo add animation manager after
        self.increment_foot=2

        self.jump_force = 10

        # for action
        self.lock = False
        self.weapon_manager = None # mettre travail de Joseph ici

        self.load_team(team)

    def load_team(self,team): ... # load all annimation in annimation manager

    def handle(self, event: pygame.event.Event):
        """methode appele a chaque event"""
        match event.type:
            case _:
                ... #* put here the future of the game like charging up or impact
        super().handle(event)

    def update(self,map,serialized,CAMERA):
        # update with 
        self.x_axis.update(Keyboard.right.is_pressed,Keyboard.left.is_pressed)
        if not self.lock:
            if Keyboard.jump.is_pressed:
                if self.grounded:
                    self.inertia.y = -self.jump_force
                    self.grounded = False
            if Keyboard.down.is_pressed:
                ...
            if Keyboard.up.is_pressed:
                ...
            if Keyboard.left.is_pressed:
                ...
            if Keyboard.right.is_pressed:
                ...
            if Keyboard.interact.is_pressed:
                ...
            if Keyboard.inventory.is_pressed:
                ...
            if Keyboard.pause.is_pressed:
                ...
            if Keyboard.end_turn.is_pressed:
                self.lock = True
                ...
                
            #* CAMERA Update of the player
            x,y = CAMERA.to_virtual(INFO.current_w/2,INFO.current_h/2 )
            _x,_y = (self.rect.left,self.rect.top)
            CAMERA.x += (_x - x)*0.0001
            CAMERA.y += (_y - y)*0.0001
            #* Effect of dezoom relatif to speed
            zoom_target = 2.5*(1/(self.actual_speed*0.1 + 1))
            CAMERA.zoom += (zoom_target - CAMERA.zoom)*0.01
            
            super().update(map,serialized)
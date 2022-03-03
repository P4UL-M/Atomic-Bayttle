import pygame
from .MOTHER import MOB
import pathlib
from tools.tools import animation_Manager, sprite_sheet

PATH = pathlib.Path(__file__).parent

class BodyPartSprite(pygame.mask.Mask):
    def __init__(self, pos,size):
        super().__init__(size,True)
        self.x, self.y = pos[0],pos[1]
    
    def collide(): ...

class Player(MOB):

    def __init__(self,name, pos, size,team):
        """parametres : 
                - x : coordonne en x du joueur
                - y : coordonne en y du joueur
                - directory : chemin absolu vers le dossier du jeu"""
        # initialisation de la classe mere permettant de faire de cette classe un sprite
        super().__init__()
        
        self.image = animation_Manager()
        self.rect = pygame.Rect(*pos,*size)
        self.increment_foot=2

        # for action
        self.lock = False
        self.weapon_manager = None # mettre travail de Joseph ici
        
        # body part with position relative to the player position
        self.body_mask = BodyPartSprite(self.rect.width * 0.25,self.rect.height * 0.1,self.rect.width * 0.5, self.rect.height*0.8)
        self.feet_mask = BodyPartSprite(self.rect.width * 0.25,self.rect.height * 0.7,self.body.w * 0.5, self.body.h*0.3)
        self.head_mask = BodyPartSprite(self.rect.width * 0.25,0,self.body.w * 0.5, self.body.h*0.3)
        self.body_left_mask = BodyPartSprite(0,self.rect.height * 0.4,self.body.w * 0.4, self.body.h*0.3)
        self.body_right_mask = BodyPartSprite(self.rect.width * 0.6,self.rect.height * 0.4,self.body.w * 0.4, self.body.h*0.3)    
  
    def load_team(self,team): ... # load all annimation in annimation manager

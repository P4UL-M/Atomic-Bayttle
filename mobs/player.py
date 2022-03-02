from turtle import position
import pygame
import time
from .MOTHER import MOB

class BodyPartSprite(pygame.sprite.Sprite):
    def __init__(self, rect, directory):
        super(BodyPartSprite, self).__init__()
        self.x=0
        self.y=0
        self.image=pygame.image.load(f"{directory}\\assets\\particle.png")
        self.image=pygame.transform.scale(self.image, (rect.w, rect.h)).convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.w=self.rect.w
        self.h=self.rect.h

class Player(MOB):

    def __init__(self, x, y, directory, id, checkpoint, Particule):
        """parametres : 
                - x : coordonne en x du joueur
                - y : coordonne en y du joueur
                - directory : chemin absolu vers le dossier du jeu"""
        # initialisation de la classe mere permettant de faire de cette classe un sprite
        MOB.__init__(self, f"player{id}", checkpoint, Particule, directory, "")

        
        action=["crouch", "attack"]
        for a in action:
            self.actions.append(a)
        self.images={}
        self.directory_assets=f"assets\\TreasureHunters\\CaptainClownNose\\Sprites\\Captain\\Captain_Sword"
        self._get_images("idle", 5, 6, "09-Idle_Sword", "Idle Sword 0")
        self.origin_compteur_image_run=8
        self._get_images('run', 6, self.origin_compteur_image_run, "Run_Sword","Run Sword 0")
        self.origin_compteur_image_fall = 6
        self._get_images("fall", 1, self.origin_compteur_image_fall, "12-Fall_Sword", "Fall Sword 0")
        self._get_images("jump", 3, 4, "11-Jump_Sword", "Jump Sword 0")  
        self._get_images("crouch", 2, 4, "13-Ground_Sword", "Ground Sword 0") 
        self._get_images("attack1", 3, 3, "15-Attack 1", "Attack 1 0") 
        self._get_images("attack2", 3, 3, "16-Attack 2", "Attack 2 0") 
        self._get_images("hurt", 4, 4, "14-Hit Sword", "Hit Sword 0") 
        self._get_images("dying", 4, 4, "07-Dead Hit", "Dead Hit 0") 
        
        self.image = self.images["idle"]["right"]["1"]
        transColor = self.image.get_at((0,0))
        self.image.set_colorkey(transColor)
        
        self.position = [x,y - self.image.get_height()]
        self.position_wave_map=[0,0]
        self.rect = self.image.get_rect()

        self.increment_foot=2
        
        self.body = pygame.Rect(0,0,self.rect.width * 0.5, self.rect.height*0.8)
        self.feet = pygame.Rect(0,0,self.body.w * 0.5, self.body.h*0.3)
        self.head = pygame.Rect(0,0,self.body.w * 0.5, self.body.h*0.3)
        self.body_left = pygame.Rect(0,0,self.body.w * 0.4, self.body.h*0.3)
        self.body_right = pygame.Rect(0,0,self.body.w * 0.4, self.body.h*0.3)

        self.body_mask = BodyPartSprite(self.body, directory)
        self.feet_mask = BodyPartSprite(self.feet, directory)
        self.head_mask = BodyPartSprite(self.head, directory)
        self.body_left_mask = BodyPartSprite(self.body_left, directory)
        self.body_right_mask = BodyPartSprite(self.body_right, directory)

        self.is_mob=False
        
        # enregistrement de l'ancienne position pour que si on entre en collision avec un element du terrain la position soit permutte avec l'anciene
        self.old_position = self.position.copy()
        self.can_attack_while_jump=True
        
        self.dico_action_functions = {
            "fall":self.chute,
            "jump":self.saut
        }       
  
    def debut_crouch(self):
        self.change_direction("crouch", self.direction)
  

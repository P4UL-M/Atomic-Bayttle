from turtle import position
import pygame
import time
from .MOTHER import MOB


class Player(MOB):

    def __init__(self, x, y, directory, zoom, id, checkpoint, Particule):
        """parametres : 
                - x : coordonne en x du joueur
                - y : coordonne en y du joueur
                - directory : chemin absolu vers le dossier du jeu"""
        # initialisation de la classe mere permettant de faire de cette classe un sprite
        MOB.__init__(self, zoom, f"player{id}", checkpoint, Particule, directory, "")

        
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
        self._get_images("crouch", 2, 1, "13-Ground_Sword", "Ground Sword 0") 
        self._get_images("attack1", 3, 3, "15-Attack 1", "Attack 1 0") 
        self._get_images("attack2", 3, 3, "16-Attack 2", "Attack 2 0") 
        self._get_images("hurt", 4, 4, "14-Hit Sword", "Hit Sword 0") 
        self._get_images("dying", 4, 4, "07-Dead Hit", "Dead Hit 0") 
        
        self.image = self.images["idle"]["right"]["1"]
        
        self.position = [x,y - self.image.get_height()]
        self.position_wave_map=[0,0]
        self.rect = self.image.get_rect()

        self.increment_foot=2
        self.feet = pygame.Rect(0,0,self.rect.width * 0.2, self.rect.height*0.1)
        self.head = pygame.Rect(0,0,self.rect.width * 0.2, self.rect.height*0.1)
        self.body = pygame.Rect(0,0,self.rect.width * 0.2, self.rect.height*0.8)
        self.body_grab_wall = pygame.Rect(0,0,self.rect.width * 0.6, self.rect.height*0.8)
        self.head_grab_wall = pygame.Rect(0,0,self.rect.width * 0.6, self.rect.height*0.1)
        self.rect_attack = pygame.Rect(0,0,self.rect.width * 0.3, self.rect.height*0.8)
        self.rect_attack_update_pos="left_right"
        self.complement_collide_wall_right = self.body.w*1.5
        self.complement_collide_wall_left = self.body.w*1.5
        self.is_mob=False
        
        # enregistrement de l'ancienne position pour que si on entre en collision avec un element du terrain la position soit permutte avec l'anciene
        self.old_position = self.position.copy()
        self.can_attack_while_jump=True
        
        #attack
        self.attack_damage={}
        self.attack_damage["attack1"]=([4,5], 10)
        self.attack_damage["attack2"]=([2,3], 10)
        self.attack_damage["dash_attack"]=([6,7],7)
        
        self.has_air_attack = False
        self.is_attacking = False
        self.a_attaquer2=False
        self.timer_attack=0
        self.cooldown_attack=1
        self.compteur_attack=0
        self.increment_attack=1
        self.compteur_attack_max=5
        self.direction_attack=""
        self.timer_attack_aerienne=0
        self.cooldown_attack_aerienne=0.5
    
        self.is_friendly=True
        
        self.dico_action_functions = {
            "fall":self.chute,
            "jump":self.saut
        }       
    
    def move_right(self, pieds_sur_sol = False): 
        self.is_mouving_x = True
        if (not self.is_attacking and not self.is_parying) or not pieds_sur_sol  or self.id != "player1":
            self.position[0] += self.speed_coeff*self.speed * self.zoom * self.speed_dt *abs(self.motion[0])
            self.update_speed()
        elif self.is_attacking:
            if self.compteur_attack < self.compteur_attack_max:
                self.compteur_attack+=self.increment_attack
                self.position[0] += self.speed *0.8* (self.compteur_attack_max/self.compteur_attack)* self.zoom * self.speed_dt *abs(self.motion[0])
                if self.compteur_attack == self.compteur_attack_max:
                    self.speed=self.speed*0.7
                    if self.speed < self.origin_speed_run:
                        self.speed=self.origin_speed_run
        if pieds_sur_sol:
            if self.action_image != "run" and self.action_image != "jump" and self.action_image != "crouch" and not self.is_attacking and not self.is_parying:
                self.change_direction("run","right") 
        if self.direction != "right":
            if self.action_image == "crouch":
                # we dont want the crouch animation du re start from the biggining
                self.change_direction(self.action_image,"right",compteur_image=self.compteur_image, current_image=self.current_image)
            elif not self.is_attacking and not self.is_parying:
                self.change_direction(self.action_image,"right")       
            else:
                self.direction="right" 

    def move_left(self, pieds_sur_sol = False): 
        self.is_mouving_x = True
        if (not self.is_attacking and not self.is_parying) or not pieds_sur_sol or self.id != "player1":
            self.position[0] -= self.speed_coeff*self.speed * self.zoom * self.speed_dt *abs(self.motion[0])
            self.update_speed()
        elif self.is_attacking:
            if self.compteur_attack < self.compteur_attack_max:
                self.compteur_attack+=self.increment_attack
                self.position[0] -= self.speed *0.8* (self.compteur_attack_max/self.compteur_attack)* self.zoom * self.speed_dt *abs(self.motion[0])
                if self.compteur_attack == self.compteur_attack_max:
                    self.speed=self.speed*0.7
                    if self.speed < self.origin_speed_run:
                        self.speed=self.origin_speed_run
        if pieds_sur_sol:
            if self.action_image != "run" and self.action_image != "jump" and self.action_image != "crouch" and not self.is_attacking and not self.is_parying:
                self.change_direction("run","left") 
        if self.direction != "left":
            if self.action_image == "crouch":
                # we dont want the crouch animation du re start from the biggining
                self.change_direction(self.action_image,"left",compteur_image=self.compteur_image, current_image=self.current_image)
            elif not self.is_attacking and not self.is_parying:
                self.change_direction(self.action_image,"left")  
            else:
                self.direction="left"
        
    def debut_attack(self):
        self.compteur_attack=0
        self.is_attacking = True
        self.change_direction("attack1", self.direction)
        self.a_attaquer2=False
        self.timer_attack=time.time()
        self.direction_attack=self.direction
    
    def attack2(self):
        self.compteur_attack=0
        self.is_attacking = True
        self.a_attaquer2=True
        self.change_direction("attack2", self.direction)
        self.direction_attack=self.direction
  
    def debut_crouch(self):
        """very simple"""
        self.change_direction("crouch", self.direction)
  

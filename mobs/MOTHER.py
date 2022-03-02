import pygame
import time
import random
from math import sqrt

class MOB(pygame.sprite.Sprite):

    def __init__(self, id, checkpoint, Particule, directory, directory_assets):
        super().__init__()
        self.directory=directory
        self.directory_assets=directory_assets
        
        self.actions = ["run", "fall", "jump", "idle", "dying", "hurt"]
        
        self.weapon=""
        
        self.checkpoint=checkpoint
        
        self.increment_foot=1
        
        self.id = id
        self.dt = 17
        self.speed_dt=17/self.dt
        
        self.images = {}
        
        # images
        self.time_cooldown_ralentissement = 0
        self.action_image = "idle"
        self.action = "idle"
        self.direction = "right"
        self.compteur_image = 0
        self.current_image = 1
        
        # course
        self.speed_coeff=1 ; self.origin_speed_run = 2.5 ; self.max_speed_run = 4.5 ; self.speed = self.origin_speed_run ; self.is_mouving_x = False
        self.compteur_image_run = 0
        self.current_image_run = 1

        # ralentissement
        self.cooldown_ralentissement = 0.2 ; self.ralentit_bool = False ; self.doit_ralentir = True ; self.compteur_ralentissement = 0
        
        # chute
        self.original_speed_gravity = 6 ; self.is_falling = False ; self.max_speed_gravity = 8 ; self.speed_gravity = self.original_speed_gravity
        self.t1_passage_a_travers_plateforme = 0
        self.cooldown_passage_a_travers_plateforme = 0.2
        self.coord_debut_chute=[0,0]
        self.timer_debut_chute=0
        self.cooldown_action_chute=0.2

        # jump
        self.a_sauter = True ; self.is_jumping = False ; self.speed_jump = 0 ; self.increment_jump = 0.25 
        self.compteur_jump_min = -4.5
        self.compteur_jump = self.compteur_jump_min
        self.compteur_jump_max = 0
        
        self.cooldown_able_to_jump = 0.1 ; self.timer_cooldown_able_to_jump = 0
        self.timer_cooldown_next_jump = 0 ; self.cooldown_next_jump = 0.2
        self.coord_debut_jump = [-999,-999]
             
        
        self.max_health=100
        self.health=self.max_health
        self.is_dead=False
        self.is_mob=True
        self.is_friendly=False
        
        self.bot=None
        
        self.motion=[1,1]
        
        self.particule=Particule(directory, self)
    
    def _get_images(self, action, nbr_image, compteur_image_max, directory_name, image_name, coefficient=1, reverse=False, weapon=""):
        try:
            dico={
                "nbr_image":nbr_image,
                "compteur_image_max":compteur_image_max,
                "right":{},
                "left":{}
                }
            if weapon=="":
                self.images[action]=dico
                d=self.images[action]
            else:
                self.all_images[weapon][action]=dico
                d=self.all_images[weapon][action]
                
            for i in range(1,nbr_image+1):
                d["right"][str(i)] = pygame.image.load(f'{self.directory}\\{self.directory_assets}\\{directory_name}\\{image_name}{i}.png').convert_alpha()
                d["right"][str(i)] = pygame.transform.scale(d["right"][str(i)], (round(d["right"][str(i)].get_width()*coefficient), round(d["right"][str(i)].get_height()*coefficient))).convert_alpha()
                d["left"][str(i)] = pygame.transform.flip(d["right"][str(i)], True, False).convert_alpha()
                if reverse: d["right"][str(i)], d["left"][str(i)] = d["left"][str(i)], d["right"][str(i)]
        except:
            print(f'{self.directory}\\{self.directory_assets}\\{directory_name}\\{image_name}{i}.png')
    
    def start_dying(self):
        self.reset_actions()
        self.change_direction("dying", self.direction)
        self.health=self.max_health
      
    def reset_actions(self, chute=False):
        """reset all actions except the fall"""
        if self.is_jumping:
            self.fin_saut()
        if self.is_attacking:
            self.is_attacking=False
        if chute:
            self.fin_chute()
        
    def take_damage(self):
        self.reset_actions()
        self.change_direction("hurt", self.direction)
  
    def update_tick(self, dt):
        """i created a multiplicator for the mouvements that based on 60 fps (clock.tick() = 17) because the original
        frame rate is 60, and so the mouvements are speeder when the game is lagging so when
        the game has a lower frame rate, same for animations but it doesnt work perfectly for animations"""
        self.dt = dt
        self.speed_dt = round(self.dt/17)
        self.particule.update_tick(dt)

    def update_speed(self):
        """appeler quand le joueur avance"""
        self.doit_ralentir = True
        # le speed augmente tant quil est plus petit que 3.5
        if self.speed < self.max_speed_run*abs(self.motion[0]):
            # aumentation du speed
            self.speed += (self.speed*0.002 + self.origin_speed_run*0.01)*abs(self.motion[0])
            if self.speed > self.max_speed_run*0.6*abs(self.motion[0]):
                if self.action_image != "idle" and self.action_image != "attack1" and self.action_image != "attack2":
                    self.images[self.action_image]["compteur_image_max"] = 6
        # vitesse maximal du defilement des images
        if self.action_image != "idle" and self.action_image != "attack1" and self.action_image != "attack2":
            self.images[self.action_image]["compteur_image_max"] = 4                    
        
    def move_left_right(self, dir, pieds_sur_sol=False):
        self.is_mouving_x = True

        x = self.speed_coeff*self.speed * self.speed_dt *abs(self.motion[0])
         
        if dir=="left": self.position[0] -= x
        else: self.position[0] += x
        self.update_speed()
        if pieds_sur_sol:
            if self.action_image != "run" and self.action_image != "jump" and self.action_image != "crouch":
                self.change_direction("run",dir) 
        if self.direction != dir:
            if self.action_image == "crouch":
                # we dont want the crouch animation du re start from the biggining
                self.change_direction(self.action_image,"right",compteur_image=self.compteur_image, current_image=self.current_image)      
            else:
                self.direction=dir    
  
    def debut_saut(self):
        #penser à bien utiliser .copy() parce que sinon la valeur est la meme que self.position tous le temps
        self.coord_debut_jump = self.position.copy()
        self.timer_cooldown_next_jump = time.time()
        self.compteur_jump = self.compteur_jump_min  
        self.is_jumping = True
        self.change_direction('jump', self.direction)

    def saut(self):
        # utilisation de la fonction carre avec un compteur qui commence en negatif et finis à 0
        # => le mouvement est RALLENTIT       
        if not self.is_attacking or self.can_attack_while_jump:
            if self.compteur_jump < self.compteur_jump_max:
                self.update_speed_jump()
                self.position[1] -= self.speed_jump*1.2
                self.compteur_jump += self.increment_jump*self.speed_dt
            else:
                self.fin_saut()
        
    def fin_saut(self):
        """reinitialisation des vvariables du saut"""
        self.is_jumping = False     
        self.a_sauter = True
        self.coord_debut_jump = [-999,-999]

    def update_speed_jump(self):
        self.speed_jump = (self.compteur_jump**2) * 0.7 * self.speed_dt
    
    def debut_chute(self):
        self.coord_debut_chute=self.position.copy()
        self.timer_cooldown_able_to_jump = time.time()
        self.is_falling = True
        #self.change_direction('fall', self.direction)
        if self.action_image=="jump":
            self.change_direction("fall", self.direction)
        self.timer_debut_chute=time.time()
        
    def chute(self):
        self.update_speed_gravity()
        self.position[1] += self.speed_gravity * self.speed_dt
        if time.time()-self.timer_debut_chute>self.cooldown_action_chute and self.action_image!="fall":
            self.change_direction("fall", self.direction)
    
    def fin_chute(self):
        self.is_falling = False
        self.speed_gravity = self.original_speed_gravity
        
        diff_x=self.position[0]-self.coord_debut_chute[0]
        diff_y=self.position[1]-self.coord_debut_chute[1]
        if sqrt(diff_x**2 + diff_y**2)>20:
            self.debut_crouch()
        if self.action_image=="fall":
            self.change_direction("idle", self.direction)
        self.coord_debut_chute=[0,0]
    
    def update_speed_gravity(self):
        if self.speed_gravity < self.max_speed_gravity:
            # self.speed_gravity augmente de plus en plus vite au file des ticks 
            self.speed_gravity += self.speed_gravity*0.005 + self.original_speed_gravity*0.005
            # reduction de la vitesse de defilement des images quand la vitesse augmente
            if self.speed_gravity > 5 and self.action_image!="idle":
                self.images[self.action_image]["compteur_image_max"] = 4
            elif self.speed_gravity > 6.5 and self.action_image!="idle":
                self.images[self.action_image]["compteur_image_max"] = 3
        # vitesse maximal du defilement des images
        elif self.images[self.action_image]["compteur_image_max"] != 2 and self.action_image!="idle":
            self.images[self.action_image]["compteur_image_max"] = 2  

    def debut_ralentissement(self):
        """methode appele quand je joueur arretes de courir"""
        # self.doit ralentir est mis sur true a chaque fois que le joueur avance et mis sur false quand il est en collision avec un mur
        if self.doit_ralentir:
            self.doit_ralentir = False
            self.ralentit_bool = True
            self.compteur_ralentissement = 0
            # augmentation du compteur pour que le ralentissement soit visible
            if not self.is_attacking:
                self.images[self.action_image]["compteur_image_max"] = 6
        else:
            # si le joueur arrete davancer mais est contre un mur
            if self.action_image == "run":
                self.change_direction("idle", self.direction)

    def ralentissement(self):
        """methode appele quand le joueur bouge pas"""
        if self.ralentit_bool:
            tab = [4, 8]
            if self.compteur_ralentissement in tab:
                # la vitesse diminue 3 fois tous les 4 frames + on fait avancer le joueur
                self.speed = self.speed*0.7 * self.speed_dt
                if self.action_image == "run":
                    if self.direction == "right":
                        self.position[0] += self.speed
                    elif self.direction == "left":
                        self.position[0] -= self.speed
                       
            self.compteur_ralentissement += 1
                
            # arret du ralentissement au bout de 8 frames
            if self.compteur_ralentissement > 8 + 1:
                self.ralentit_bool = False
                if self.action_image == "run":
                    self.change_direction("idle", self.direction)
                
    def save_location(self): 
        """enregistrement de la position dans 'old_position'"""
        self.old_position = self.position.copy()
    
    def move_back(self):
        """retour aux coordonees de la frame davant"""
        self.position = self.old_position
        self.doit_ralentir = False

    def update_animation(self):
        """change les animations du joueurs, appelé toutes les frames"""
        # changement de l'image tout les X ticks
        
        if self.compteur_image < self.images[self.action_image]["compteur_image_max"]:
            if self.action_image == "run":
                self.compteur_image += 1*self.speed_dt * abs(self.motion[0])
                self.compteur_image_run = self.compteur_image
                self.current_image_run = self.current_image
            else:
                self.compteur_image += 1*self.speed_dt
        else:
            # temp sert a faire en sorte que l'image ne soit pas update si on passe de 'uptofall' à 'fall'
            temp = False
            # changement de l'image
            self.compteur_image = 0
            # si l'image en cours est la derniere on re passe a la 1ere, sinon on passe a la suivante
            if self.current_image < self.images[self.action_image]["nbr_image"]:
                self.current_image += 1
            else:
                temp=True
                # pour ces actions on passe a une autre animation quand l'animation respeective est finis
                # it doesnt matter if the mob doesnt have these actions
                if self.action_image == "crouch":
                    if self.is_mouving_x:
                        self.change_direction("run", self.direction)
                    else:
                        self.change_direction("idle", self.direction)
                elif self.action_image=="hurt"or self.action_image=="air_attack":
                    self.is_attacking=False
                    self.is_parying=False
                    if not self.is_falling:
                        self.change_direction("idle", self.direction)
                    else:
                        if "up_to_fall" in self.actions :self.change_direction("up_to_fall", self.direction)
                        else: self.change_direction("fall", self.direction)
                elif self.action_image=="dying":
                    self.position=[self.checkpoint[0], self.checkpoint[1]-self.image.get_height()]
                    self.fin_chute()
                    self.change_direction("idle", self.direction)
                else:
                    temp=False
                    self.current_image = 1
            
            if not temp:
                self.image = self.images[self.action_image][self.direction][str(self.current_image)]
                transColor = self.image.get_at((0,0))
                self.image.set_colorkey(transColor)
        
    def change_direction(self, action, direction, compteur_image=0, current_image=0):
        """change la direction et / ou l'action en cours"""
        if action != "attack1" and action != "attack2" and action != "up_to_attack" and action != "air_attack":
            self.is_attacking=False
        elif self.action == "attack2":
            self.a_attaquer2=False
            
        # ralentissement si le joueur cours et continue de courir dans lautre sens
        if self.action_image == "run" and action == "run":
            self.speed *= 0.9
        # reset du compteur d'image si le joueur ne va pas chuter, sion il garde sa vitesse
        if self.action_image == "run" and action != "fall" and action != "up_to_fall":
            self.images["run"]["compteur_image_max"] = self.origin_compteur_image_run
        elif self.action_image == "fall":
            self.images["fall"]["compteur_image_max"] = self.origin_compteur_image_fall
        self.action_image = action
        self.direction = direction
        self.compteur_image = compteur_image
        self.current_image = current_image
        self.image = self.images[self.action_image][self.direction]["1"]
        transColor = self.image.get_at((0,0))
        self.image.set_colorkey(transColor)

    def update_coord_rect(self):
        # update des coordonees des rect
        self.rect.topleft = self.position
        self.body.midbottom = self.rect.midbottom
        self.feet.midbottom = (self.body.midbottom[0], self.body.midbottom[1]-self.increment_foot)
        self.head.midtop = self.body.midtop
        self.body_left.midleft=self.body.midleft
        self.body_right.midright=self.body.midright

        self.body_mask.rect.topleft = self.body.topleft
        self.feet_mask.rect.topleft = self.feet.topleft
        self.head_mask.rect.topleft = self.head.topleft
        self.body_left_mask.rect.topleft = self.body_left.topleft
        self.body_right_mask.rect.topleft = self.body_right.topleft

    def update(self):
        """methode appele a chaque tick"""
        if self.speed > self.max_speed_run:
            if self.action != "jump_edge" and self.action != "chute":
                self.speed = self.max_speed_run
            else:
                self.speed *= 0.97
            
        self.update_animation()
        
        self.update_coord_rect()
        
        # la vitesse de course du joueur ne ralentit pas tant qu'il coure ou chute
        if self.action_image == "run" or self.action_image == "fall" or self.action_image == "up_to_fall" or self.action_image == "jump":
            self.time_cooldown_ralentissement = time.time()
        
        if self.action_image == "idle" and time.time() - self.time_cooldown_ralentissement > self.cooldown_ralentissement:
            self.speed = self.origin_speed_run

    def update_action(self):
        """sometimes actions and actions image are differents :
        when the player dash self.action = 'dash' and self.action_image = 'jump'
        because its has the same image, so we update it here"""
        if self.action_image in ["fall", "dying", "jump"]:
            self.action = self.action_image
        else:
            for i in ["run", "crouch", "idle"]:
                if i == self.action_image:
                    if self.is_falling:
                        self.action="fall"
                    else:
                        self.action=i
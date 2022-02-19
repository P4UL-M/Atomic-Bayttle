import pygame
import os
from pygame.locals import *
from map.render_map import RenderMap
from entities_sprite.particule import Particule
from mobs.player import Player
from mobs.mob_functions import *
from mobs.collision import Collision
from map.object_map import Object_map
from physique import *

pygame.init()

GAME = None
CAMERA = None

class Game:
    def __init__(self):
        self.directory = os.path.dirname(os.path.realpath(__file__))
        
        info_screen = pygame.display.Info() #taille de l'écran
        self.screen = pygame.display.set_mode((round(info_screen.current_w*0.8),round(info_screen.current_h*0.8)))
        self.screen.fill((200,100,100))       
        self.bg = pygame.Surface((self.screen.get_width(), self.screen.get_height()), flags=SRCALPHA)
        self.dt = 1/30
        
        self.all_mobs=[]
        self.group = pygame.sprite.Group()
        self.group_particle = pygame.sprite.Group()
        self.group_object=pygame.sprite.Group()
        self.group_object=pygame.sprite.Group()
        self.all_groups = [self.group_object, self.group_object, self.group, self.group_particle]
        
        self.render=RenderMap(self.screen.get_width(), self.screen.get_height(), self.directory)
        self.map_height=self.render.get_height()
        self.map_width=self.render.get_width()
        player_position = self.render.dico["spawn_player"]
        
        coord = self.render.dico["spawn_player"]
        self.mortier=Object_map(self.render.zoom, "mortier", coord[0], coord[1], self.directory, 1, 100, "assets\\TheUltimateWeaponsPack", "mortier", 2, 30, 0)
        self.group_object.add(self.mortier)
        
        self.checkpoint=[player_position[0], player_position[1]+1] # the plus one is because the checkpoints are 1 pixel above the ground
        self.player=Player(player_position[0], player_position[1]+1, self.directory, self.render.zoom, "1", self.checkpoint.copy(), Particule)
        
        self.pressed_up_bool = [False]
        self.last_player_position=self.player.position.copy()
        
        self.scroll=[0,0]
        self.scroll_rect = Rect(self.player.position[0],self.player.position[1],1,1)
        
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        self.motion = [0, 0]
        
        self.add_mob_to_game(self.player, "solo_clavier")
        self.add_mob_to_game(self.player, "solo_clavier", group="wave")
        
        self.collision=Collision(self.render.zoom, self.render.dico) 
        
        self.all_controls={}
        self.all_controls["solo_clavier"]={"perso":[],"touches":[pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP,pygame.K_DOWN, pygame.K_q, pygame.K_a, pygame.K_d, pygame.K_z, pygame.K_e, pygame.K_u, pygame.K_i, pygame.K_o]}  
    
    def blit_group(self, bg, all_groups):
        """blit les images des sprites des groupes sur la surface bg"""
        for group in all_groups:
            for sprite in group.sprites():
                if self.scroll_rect.x - (self.screen.get_width()/2) - sprite.image.get_width() <= sprite.position[0] <= self.scroll_rect.x + (self.screen.get_width()/2)  + sprite.image.get_width() and \
                    self.scroll_rect.y - (self.screen.get_height()/2) - sprite.image.get_height() <= sprite.position[1] <= self.scroll_rect.y + (self.screen.get_height()/2)  + sprite.image.get_height():
                        new_x=self.screen.get_width()/2 + sprite.position[0] - self.scroll_rect.x
                        new_y = self.screen.get_height()/2 + sprite.position[1] - self.scroll_rect.y
                        bg.blit(sprite.image, (new_x,new_y))
    
    def update_camera(self, playerx, playery, player_speed_dt):
        self.scroll[0] = ((playerx - self.scroll_rect.x) // 15)*self.render.zoom*player_speed_dt
        self.scroll_rect.x += self.scroll[0] 
        self.scroll[1] = ((playery - self.scroll_rect.y) // 15)*self.render.zoom*player_speed_dt
        self.scroll_rect.y += self.scroll[1]
    
    def add_mob_to_game(self, mob, input, group="base"):
        if group=="base":
            self.all_mobs.append([mob, input])
            self.group.add(mob)

    def handle_input(self):
        """agit en fonction des touches appuye par le joueur"""
             
        pressed = pygame.key.get_pressed()
        self.all_controls["solo_clavier"]["perso"]=[]
        perso_manette=[]
        if pressed:
            for mob in self.all_mobs:
                if mob[0].action_image!="dying":
                    #le joueur joue au clavier
                    # elif player[1]=="manette":
                    #     perso_manette.append(player[0])
                    if mob[1] in self.all_controls.keys():
                        self.all_controls[mob[1]]["perso"].append(mob[0])
                    elif mob[1]=="manette":
                        perso_manette.append(mob[0])
                    elif mob[1]=="bot":
                        if mob[0].bot.get_distance_target()<750*self.render.zoom:
                            mob[0].bot.make_mouvement(self.collision)
                        else:
                            mob[0].reset_actions()
            
            for control in self.all_controls.values():
                if pressed[control["touches"][0]]: pressed_left(control["perso"], self.collision)
                elif pressed[control["touches"][1]]: pressed_right(control["perso"], self.collision)
                if not pressed[control["touches"][0]] and not pressed[control["touches"][1]]:
                    for mob in control["perso"]:
                        handle_input_ralentissement(mob)
                if pressed[control["touches"][2]]:pressed_up(control["perso"], pressed[control["touches"][3]], pressed[control["touches"][0]], pressed[control["touches"][1]], self.pressed_up_bool, self.collision)
                if pressed[control["touches"][3]]:pressed_down(control["perso"], self.collision)
                if pressed[control["touches"][4]]:pass
                if pressed[control["touches"][5]]:pressed_attack(control["perso"])
                if pressed[control["touches"][6]]:pass     
                if pressed[control["touches"][7]]:pass                                                 
                if pressed[control["touches"][8]]: 
                    id = pressed_interact(control["perso"], self.group_object)
                    if id !=None:
                        self.interact_object_map(id)
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    
    def gestion_chute(self, mob):
        # si le j saut ou dash la chute prends fin
        if mob.is_jumping and mob.is_falling:
            mob.fin_chute(jump_or_dash = True) 
        
        # si le joueur n'est pas sur un sol et ne chute pas on commence la chute
        if not self.collision.joueur_sur_sol(mob):
            if not mob.is_falling and not mob.is_jumping:
                mob.debut_chute()
        else:
            # sinon on stop la chute si il y en a une
            if mob.is_falling:
                mob.fin_chute()
    
    def interact_object_map(self, id):
        if id =="mortier":
            print("coucou")
    
    def update_particle(self):
        """update les infos concernant les particles, ajoute ou en supprime """
        # si l'action du joueur a changer on l'update dans la classe particule
        
        for mob in [i[0] for i in self.all_mobs]:
            mob.particule.update()
                
            # transmition de donnee a travers des tableau de lobjet de la classe particle vers la clsse game    
            if mob.particule.new_particle != []:
                for i in mob.particule.new_particle:
                    self.group_particle.add(i)
                mob.particule.new_particle.clear()
                
            if mob.particule.remove_particle != []:
                for id in mob.particule.remove_particle:
                    for sprite in self.group_particle.sprites():
                        if sprite.id == f"particule{id}":
                            self.group_particle.remove(sprite)
                mob.particule.remove_particle.clear() 
    
    def handle_action(self, mob):
        
        if mob.is_jumping and self.collision.joueur_se_cogne(mob):
            mob.fin_saut()
            
        if mob.is_jumping and self.collision.joueur_sur_sol(mob, ground_only=True) and mob.compteur_jump>mob.compteur_jump_min+mob.increment_jump*3:
            mob.debut_crouch()
            mob.fin_saut()

        # gestion collision avec les murs
        
        mob.save_location()    
        
        if mob.position[1] > self.map_height + 100:
            mob.position = [mob.checkpoint[0], mob.checkpoint[1]-mob.image.get_height()]
        
        self.gestion_chute(mob) 

        mob.update_action()
        
    def update(self):
        """ fonction qui update les informations du jeu"""   
                
        for group in self.all_groups:
            group.update()
            
        for mob in [tuple[0] for tuple in self.all_mobs]:
            if mob.bot == None or mob.bot.get_distance_target()<750*self.render.zoom:
                mob.update_action()
                self.handle_action(mob)
                
                if mob.action in mob.dico_action_functions.keys():
                    mob.dico_action_functions[mob.action]()
                    
                if mob.is_jumping and mob.action=="run":
                    mob.is_jumping=False
            else:
                mob.reset_actions()
        
        self.update_particle()      
        
        self.update_camera(self.player.position[0], self.player.position[1], self.player.speed_dt)

    def update_ecran(self):     
        self.bg.fill((255,155,155))
        self.render.render(self.bg, self.scroll_rect.x, self.scroll_rect.y)
        self.blit_group(self.bg, self.all_groups)
        self.screen.blit(self.bg, (0,0))
        self.last_player_position=self.player.position.copy()
    
    def run(self):
        """boucle du jeu"""

        clock = pygame.time.Clock()

        self.running = True
        while self.running:
            
            self.player.is_mouving_x = False
            self.handle_input()
            self.update()
            self.update_ecran()
            
            x0=self.mortier.position[0] + self.mortier.image.get_width()/2
            h0=self.mortier.position[1] + self.mortier.image.get_width()/2
            v0=8.2
            from math import pi
            a=pi/4

            for t in range(1, 1000):
                x=get_x(t/10, v0, a)
                y=get_y(x, v0, a, h0)
                x=x*v0+x0
                if self.scroll_rect.x - (self.screen.get_width()/2) <= x <= self.scroll_rect.x + (self.screen.get_width()/2) and \
                    self.scroll_rect.y - (self.screen.get_height()/2) <= y <= self.scroll_rect.y + (self.screen.get_height()/2):
                        new_x=self.screen.get_width()/2 + x - self.scroll_rect.x
                        new_y = self.screen.get_height()/2 + y - self.scroll_rect.y
                        pygame.draw.circle(self.screen, (255, 0, 0), (new_x, new_y), 3)
            
            a=pi/6            
            for t in range(1, 1000):
                x=get_x(t/10, v0, a)
                y=get_y(x, v0, a, h0)
                x=x*v0+x0
                if self.scroll_rect.x - (self.screen.get_width()/2) <= x <= self.scroll_rect.x + (self.screen.get_width()/2) and \
                    self.scroll_rect.y - (self.screen.get_height()/2) <= y <= self.scroll_rect.y + (self.screen.get_height()/2):
                        new_x=self.screen.get_width()/2 + x - self.scroll_rect.x
                        new_y = self.screen.get_height()/2 + y - self.scroll_rect.y
                        pygame.draw.circle(self.screen, (0, 255, 0), (new_x, new_y), 3)
            
            
            a=(2*pi)/6
            for t in range(1, 1000):
                x=get_x(t/10, v0, a)
                y=get_y(x, v0, a, h0)
                x=x*v0+x0
                if self.scroll_rect.x - (self.screen.get_width()/2) <= x <= self.scroll_rect.x + (self.screen.get_width()/2) and \
                    self.scroll_rect.y - (self.screen.get_height()/2) <= y <= self.scroll_rect.y + (self.screen.get_height()/2):
                        new_x=self.screen.get_width()/2 + x - self.scroll_rect.x
                        new_y = self.screen.get_height()/2 + y - self.scroll_rect.y
                        pygame.draw.circle(self.screen, (0, 0, 255), (new_x, new_y), 3)
            
            pygame.display.update()      
            
            self.dt = clock.tick(60) #faire calcul en % fonction inverse 60/60 is normal factor 60/40 is new factor if 40fps
            for mob in [tuple[0] for tuple in self.all_mobs]:
                mob.update_tick(self.dt)

        pygame.quit()
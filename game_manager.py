import pygame
import os
from pygame.locals import *
from map.render_map import RenderMap
from entities_sprite.particule import Particule
from mobs.player import Player
from mobs.mob_functions import *
from mobs.collision import Collision
#from map.object_map import Object_map
from weapons.physique import *

GAME = None
CAMERA = None

class Partie:
    def __init__(self,j1,j2):
        
        self.screen = pygame.Surface((1600,900))    
        self.bg = pygame.image.load
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
        
        self.checkpoint=[600, -300] # the plus one is because the checkpoints are 1 pixel above the ground
        self.player= Player(600, -300, self.directory, "1", self.checkpoint.copy(), Particule)
        
        self.last_player_position=self.player.position.copy()
        
        """
        A passer dans keyboard si possible
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        self.motion = [0, 0]"""
        
        self.add_mob_to_game(self.player, "solo_clavier")
        
        # à revoir
        self.collision=Collision(self.render.map)
    
    def blit_group(self, bg, all_groups):
        """blit les images des sprites des groupes sur la surface bg"""
        for group in all_groups:
            for sprite in group.sprites():
                    bg.blit(sprite.image, sprite.position)
    
    """ a faire par le player de preference
    def update_camera(self, playerx, playery, player_speed_dt):
        CAMERA.x = ((playerx - self.scroll_rect.x) // 15)*player_speed_dt
        self.scroll_rect.x += self.scroll[0]
        CAMERA.y= ((playery - CAMERA.y) // 15)*player_speed_dt"""
    
    def add_mob_to_game(self, mob, input, group="base"):
        if group=="base":
            self.all_mobs.append([mob, input]) #TODO revoir syteme des input, inclu à mob et pas extérieur
            self.group.add(mob)

    def handle_input(self): #! Système des action entier a revoir
        """agit en fonction des touches appuye par le joueur"""
             
        pressed = pygame.key.get_pressed()
        self.all_controls["solo_clavier"]["perso"]=[]
        perso_manette=[]
        if pressed: #! condition inutile pressed est un dictionnaire et jamais vide
            for mob in self.all_mobs:
                if mob[0].action_image!="dying": #! need to délier annimation et action
                    #le joueur joue au clavier
                    # elif player[1]=="manette":
                    #     perso_manette.append(player[0])
                    if mob[1] in self.all_controls.keys(): #? pk mob est un dictionaire et pas une classe c'est pas le joueur
                        self.all_controls[mob[1]]["perso"].append(mob[0])
                    elif mob[1]=="manette":
                        perso_manette.append(mob[0])
                    elif mob[1]=="bot": #? ça c'est pour quand t'es un bot c'est ça ? pk tu le range pas dans la classe directement et que y a des array et des dico de partout
                        if mob[0].bot.get_distance_target()<750:
                            mob[0].bot.make_mouvement(self.collision)
                        else:
                            mob[0].reset_actions()
            
            for control in self.all_controls.values():
                if pressed[control["touches"][0]]: pressed_left(control["perso"], self.collision) #! ajouter les action dans le nom des method et pas les touche 
                elif pressed[control["touches"][1]]: pressed_right(control["perso"], self.collision)
                if not pressed[control["touches"][0]] and not pressed[control["touches"][1]]:
                    for mob in control["perso"]:
                        handle_input_ralentissement(mob)
                if pressed[control["touches"][2]]:pressed_up(control["perso"], pressed[control["touches"][3]], pressed[control["touches"][0]], pressed[control["touches"][1]], self.pressed_up_bool, self.collision)
                if pressed[control["touches"][3]]:pressed_down(control["perso"], self.collision)
                if pressed[control["touches"][5]]:pressed_attack(control["perso"])                                             
                if pressed[control["touches"][8]]: #! pas d'interaction prévu avec des objets sur la map a virer
                    id = pressed_interact(control["perso"], self.group_object)
                    if id !=None:
                        self.interact_object_map(id)
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    
    """ keske ça fou dans game xd
    def gestion_chute(self, mob):
        # si le j saut ou dash la chute prends fin
        if mob.is_jumping and mob.is_falling:
            mob.fin_chute() 
        
        # si le joueur n'est pas sur un sol et ne chute pas on commence la chute
        if not self.collision.joueur_sur_sol(mob):
            if not mob.is_falling and not mob.is_jumping:
                mob.debut_chute()
        else:
            # sinon on stop la chute si il y en a une
            if mob.is_falling:
                mob.fin_chute()"""
    
    """pas au role de game
    def interact_object_map(self, id):
        if id =="mortier":
            print("coucou")"""
    
    """faire passer les particule par un script tier
    def update_particle(self):
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
    """

    def handle_action(self, mob): #! pas le role de game non plus le joueur doit se demerder
        
        if mob.is_jumping and self.collision.joueur_se_cogne(mob):
            mob.fin_saut()

        if mob.is_jumping and mob.action_image=="crouch":
            mob.fin_saut()
        
        if mob.action_image=="jump" and not mob.is_jumping:
            mob.change_direction("idle", mob.direction)

        # gestion collision avec les murs
        
        mob.save_location()    
        
        if mob.position[1] > self.map_height + 100:
            mob.position = [mob.checkpoint[0], mob.checkpoint[1]-mob.image.get_height()]
        
        self.gestion_chute(mob) 

        mob.update_action()
        
    def update(self):
        """ fonction qui update les informations du jeu"""   
                
        for group in self.all_groups:
            group.update() #? appelle le update des mob ?
            
        for mob in [tuple[0] for tuple in self.all_mobs]:
            if mob.bot == None or mob.bot.get_distance_target()<750: #? système de bot pk pas mais pas comme ça
                mob.update_action()
                self.handle_action(mob)
                
                if mob.action in mob.dico_action_functions.keys():
                    mob.dico_action_functions[mob.action]()
                    
                if mob.is_jumping and mob.action=="run": #? run genre run ou juste marcher ? pk on annule le saut si on marche ? pk on traite les action puis on les annulent après
                    mob.is_jumping=False
            else:
                mob.reset_actions()
        
        self.update_particle()      
        
        self.update_camera(self.player.position[0], self.player.position[1], self.player.speed_dt)

    def Draw(self):     
        self.render.render(self.bg, self.scroll_rect.x, self.scroll_rect.y, self.scroll_rect)
        self.blit_group(self.bg, self.all_groups)
        self.screen.blit(self.bg, (0,0))
        self.last_player_position=self.player.position.copy()
    
    def test_parabole(self):
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

    def run(self):
        """boucle du jeu"""

        clock = pygame.time.Clock()

        self.running = True
        while self.running:
            self.player.is_mouving_x = False
            self.collision.joueur_sur_sol(self.player, first=True)
            self.handle_input()
            self.update()
            self.update_ecran()
            
            self.test_parabole()
            
            pygame.display.update()      
            
            self.dt = clock.tick(60)
            for mob in [tuple[0] for tuple in self.all_mobs]:
                mob.update_tick(self.dt)

        pygame.quit()
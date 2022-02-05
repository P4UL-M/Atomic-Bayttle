import pygame
import time
import random
from pygame.locals import *
import math

class LittleParticle(pygame.sprite.Sprite):
    """ class d'une particle qui apparait lors du dash du joueur"""
    def __init__(self, x, y, nbr, directory, zoom, speed_dt, alpha):
        super().__init__()
        self.id = f"particule{nbr}"
        
        taille = random.randint(1,5)
        
        self.zoom = zoom
        self.speed_dt = speed_dt

        self.image = pygame.image.load(f'{directory}\\assets\\particle.png')
        self.image = pygame.transform.scale(self.image, (taille*self.zoom, taille*self.zoom))

        self.position = [x,y-self.image.get_height()]
        self.rect = self.image.get_rect()

        # la particle disparait apres le cooldown
        self.t1 = time.time()
        self.cooldown = random.uniform(0.2, 0.8)
        
        self.speedx = math.cos(alpha)*self.zoom*self.speed_dt
        self.speedy = math.sin(alpha)*self.zoom*self.speed_dt
            
    def update(self):
        self.position[0] += self.speedx
        self.position[1] -= self.speedy
        self.rect.topleft = self.position
        
class Particule:
    """ MAIN CLASS OF THE SCRIPT"""
    def __init__(self, directory, player, zoom):
        self.zoom = zoom
        self.dt = 17
        self.speed_dt = round(self.dt/17)
        self.player=player
        self.directory = directory
        self.number_particule = 0
        self.pieds_collide_jump_edge = False
        self.all_particle={}
        # key : id | value : object of class LittleParticle
        self.all_particle["run"] = {}
        self.all_particle["jump"] = {}
        self.all_particle["dash"] = {}
        self.all_particle["wall_slide"] = {}
        self.all_particle["jump_edge"]= {}
        self.all_particle["ground_slide"] = {}
        # value : object of class LittleParticle
        self.new_particle = []
        # value : id of the particle
        self.remove_particle = []
    
    def update_tick(self, dt):
        self.dt = dt
        self.speed_dt = round(self.dt/17)
    
    def add_particle_base_mouvement(self,dico_name, p):
        self.number_particule += 1
        self.all_particle[dico_name][str(self.number_particule)] = p
        self.new_particle.append(p)    
    
    def spawn_particle(self, action):
        """action : (str) the action of the player
        add particles to the dictionnarie that is in self.all_particles"""
        # pour eviter des chiffres trop grands qui prendrait trop de memoire
        if self.number_particule > 1500:
            self.number_particule = 0
        
        if self.player.direction=="right":x=self.player.position[0]+15*self.zoom
        else:x=self.player.position[0]+self.player.rect.w-15*self.zoom
        y=self.player.position[1]+self.player.rect.h
            
        if action == "run" or action == "crouch":
            if self.player.direction=="left":self.add_particle_base_mouvement("run", LittleParticle(x, y, self.number_particule, self.directory, self.zoom, self.speed_dt, random.uniform(0, math.pi/4)))
            elif self.player.direction=="right":self.add_particle_base_mouvement("run", LittleParticle(x, y, self.number_particule, self.directory, self.zoom, self.speed_dt, random.uniform(math.pi, 3*math.pi/4)))
            
        elif action == "jump":
            # reajustement de la position des particles
            if self.player.direction == "right": c = 55*self.zoom
            elif self.player.direction == "left": c = self.player.rect.w-55*self.zoom
            # apparition de deux particles, une a gauche et une a droite
            self.add_particle_base_mouvement("jump", LittleParticle(self.player.coord_debut_jump[0]+c, self.player.coord_debut_jump[1]+self.player.rect.h,self.number_particule, self.directory, self.zoom, self.speed_dt, random.uniform(0, math.pi/4)))
            self.add_particle_base_mouvement("jump", LittleParticle(self.player.coord_debut_jump[0]+c, self.player.coord_debut_jump[1]+self.player.rect.h,self.number_particule, self.directory, self.zoom, self.speed_dt, random.uniform(3*math.pi/4, math.pi)))

        elif action == "dash":
            alpha=-99
            if self.player.direction == "right": c = 55*self.zoom
            elif self.player.direction == "left": c = self.player.rect.w-55*self.zoom
            if self.player.dash_direction_y == "up" and self.player.dash_direction_x == "right": alpha = random.uniform(3*math.pi/4, 7*math.pi/4)
            elif self.player.dash_direction_y == "down" and self.player.dash_direction_x == "right": alpha = random.uniform(math.pi/4, 5*math.pi/4)
            elif self.player.dash_direction_y == "up" and self.player.dash_direction_x == "left": alpha = random.uniform((-3)*math.pi/4, math.pi/4)
            elif self.player.dash_direction_y == "down"and self.player.dash_direction_x == "left": alpha = random.uniform((-1)*math.pi/4, 3*math.pi/4)
            elif self.player.dash_direction_x == "left" and self.player.dash_direction_y == "": alpha = random.uniform(-math.pi/2, math.pi/2)
            elif self.player.dash_direction_x == "right" and self.player.dash_direction_y == "": alpha = random.uniform(math.pi/2, 3*math.pi/2)
            elif self.player.dash_direction_x == "" and self.player.dash_direction_y == "up": alpha = random.uniform((-1)*math.pi, 0)
            elif self.player.dash_direction_x == "" and self.player.dash_direction_y == "down": alpha = random.uniform(0, math.pi)
            if alpha!=-99:
                for _ in range(4):
                    self.add_particle_base_mouvement("dash", LittleParticle(self.player.coord_debut_dash[0]+c, self.player.coord_debut_dash[1]+self.player.rect.h, self.number_particule, self.directory, self.zoom, self.speed_dt, alpha))
        
        elif action == "Wall_slide":
            if self.player.direction == "right": c=9*self.zoom       
            elif self.player.direction == "left": c=47*self.zoom-self.player.rect.w
            if self.player.direction=="right":self.add_particle_base_mouvement("wall_slide", LittleParticle(x + self.player.body.w +c, y - self.player.body.h,self.number_particule, self.directory, self.zoom, self.speed_dt, random.uniform(math.pi/2, math.pi)))
            elif self.player.direction=="left": self.add_particle_base_mouvement("wall_slide", LittleParticle(x + self.player.body.w +c, y - self.player.body.h,self.number_particule, self.directory, self.zoom, self.speed_dt, random.uniform(0, math.pi/2)))
        
        elif action == 'jump_edge':
            # apparition de deux particles, une a gauche et une a droite
            if self.player.direction_jump_edge=="left":
                self.add_particle_base_mouvement("jump_edge", LittleParticle(self.player.coord_debut_jump_edge[0]+76*self.zoom, self.player.coord_debut_jump_edge[1]+self.player.rect.h, self.number_particule, self.directory, self.zoom, self.speed_dt, random.uniform(math.pi/2, math.pi)))
                self.add_particle_base_mouvement("jump_edge", LittleParticle(self.player.coord_debut_jump_edge[0]+76*self.zoom, self.player.coord_debut_jump_edge[1]+self.player.rect.h, self.number_particule, self.directory, self.zoom, self.speed_dt, random.uniform(math.pi/2, 3*math.pi/2)))
            elif self.player.direction_jump_edge=="right":
                self.add_particle_base_mouvement("jump_edge", LittleParticle(self.player.coord_debut_jump_edge[0]+54*self.zoom, self.player.coord_debut_jump_edge[1]+self.player.rect.h, self.number_particule, self.directory, self.zoom, self.speed_dt, random.uniform(0, math.pi/2)))
                self.add_particle_base_mouvement("jump_edge", LittleParticle(self.player.coord_debut_jump_edge[0]+54*self.zoom, self.player.coord_debut_jump_edge[1]+self.player.rect.h, self.number_particule, self.directory, self.zoom, self.speed_dt, random.uniform(0, -math.pi/2)))
        
        elif action == 'ground_slide':
            self.add_particle_base_mouvement("ground_slide",LittleParticle(x, y, self.number_particule, self.directory, self.zoom, self.speed_dt, random.uniform(0, math.pi/4)))
                   
    def update(self):
        """methode appeler a chaque tick"""
        # when the seconds between now and the apparition of the particle > its cooldown of lifetime : 
        # the particle is add in self.remove_particle and remove from the dictionnarry of the mouvement
        id_a_sup = []
        for dico in self.all_particle.values():
            for id,p in dico.items():
                if time.time() - p.t1 > p.cooldown:
                    self.remove_particle.append(id)
                    id_a_sup.append(int(id))
            for i in id_a_sup:
                del dico[str(i)]
            id_a_sup.clear()

        # when the dictonnarie of the current mouvement are not 'full' we add particles in it
        if self.player.action == "run" and len(self.all_particle["run"]) < 20: self.spawn_particle("run")
        elif self.player.action == "crouch" and len(self.all_particle["run"]) < 10: self.spawn_particle("run")
        elif self.player.action == "jump" and len(self.all_particle["jump"]) < 30: self.spawn_particle("jump")
        elif self.player.action == "dash" and len(self.all_particle["dash"]) < 30: self.spawn_particle("dash")
        elif self.player.action == "Wall_slide" and len(self.all_particle["wall_slide"]) < 20: self.spawn_particle("Wall_slide")
        elif self.player.action == "jump_edge" and len(self.all_particle["jump_edge"]) < 20 and self.pieds_collide_jump_edge: self.spawn_particle("jump_edge")
        elif self.player.action == "ground_slide" and len(self.all_particle["ground_slide"]) < 20: self.spawn_particle("ground_slide")
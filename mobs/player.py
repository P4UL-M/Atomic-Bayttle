import pygame
from .MOTHER import MOB
import pathlib
from tools.tools import animation_Manager, sprite_sheet,Keyboard,Vector2
from entities_sprite.particule import Particule

PATH = pathlib.Path(__file__).parent.parent
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

        self.manager:animation_Manager = animation_Manager()
        #self.image.fill((255,0,0)) #! tempo add animation manager after
        self.increment_foot=2
        self.rigth_direction = True

        self.jump_force = 8
        self.double_jump = 0
        self.jump_cooldown = 0
        self.cooldown_double_jump = 400

        # for action
        self.lock = False
        self.weapon_manager = None # mettre travail de Joseph ici

        self.load_team(team)

    @property
    def image(self) -> pygame.Surface:
        surf = self.manager.surface
        if self.rigth_direction:
            return surf
        else:
            return pygame.transform.flip(surf,True,False) #! if too much loss of perf we will stock both

    def load_team(self,team):
        idle = sprite_sheet(PATH / "assets" / "perso"/ team / "idle.png",(24,28)) # load all annimation in annimation manager
        run = sprite_sheet(PATH / "assets" / "perso"/ team /  "run.png",(25,30)) # load all annimation in annimation manager
        jump = sprite_sheet(PATH / "assets" / "perso"/ team /  "jump.png",(25,30)) # load all annimation in annimation manager
        fall = sprite_sheet(PATH / "assets" / "perso"/ team /  "fall.png",(25,28)) # load all annimation in annimation manager
        ground = sprite_sheet(PATH / "assets" / "perso"/ team /  "ground.png",(26,28)) # load all annimation in annimation manager
        self.manager.add_annimation("idle",idle,10)
        self.manager.add_annimation("run",run,10)
        self.manager.add_annimation("jump",jump,5)
        self.manager.add_annimation("fall",fall,10)
        self.manager.add_annimation("ground",ground,15)
        self.manager.add_link("jump","fall")
        self.manager.add_link("ground","idle")
        self.manager.load("run")

    def handle(self, event: pygame.event.Event):
        """methode appele a chaque event"""
        match event.type:
            case _:
                ... #* put here the future of the game like charging up or impact
        super().handle(event)

    def update(self,map,serialized,CAMERA,particle_group):
        if not self.lock:
            self.x_axis.update(Keyboard.right.is_pressed,Keyboard.left.is_pressed)
            if Keyboard.jump.is_pressed:
                if self.grounded or (self.jump_cooldown< pygame.time.get_ticks() and self.double_jump):
                    self.double_jump = (self.inertia.y < 1 and self.inertia.y > 0) or self.grounded # this is like grounded but constant because sometime we are on the ground but not colliding because gravity too weak
                    self.inertia.y = -self.jump_force
                    self.grounded = False
                    self.jump_cooldown = pygame.time.get_ticks() + self.cooldown_double_jump
                    self.manager.load("jump")
                    for i in range(5):
                        particle_group.add(Particule(10,Vector2(self.rect.left + self.image.get_width()//2,self.rect.bottom),self.image.get_width()//2,Vector2(1,-2),2,True))
            if Keyboard.down.is_pressed:
                ...
            if Keyboard.up.is_pressed:
                ...
            if Keyboard.left.is_pressed:
                ...
            if Keyboard.right.is_pressed:
                ...
            if Keyboard.interact.is_pressed:
                map.add_damage(Vector2(self.rect.left,self.rect.top),50)
            if Keyboard.inventory.is_pressed:
                ...
            if Keyboard.pause.is_pressed:
                ...
            if Keyboard.end_turn.is_pressed:
                self.lock = True
                ...

            if self.x_axis.value>0:
                self.rigth_direction = True
            elif self.x_axis.value<0:
                self.rigth_direction = False

            if self.manager._loaded_name not in ["jump","ground"]:
                if self.actual_speed>1:
                    if (self.inertia.y > 1.5 or self.inertia.y < 0) and not self.grounded:
                        self.manager.load("fall")
                    elif self.manager._loaded_name == "fall":
                        self.manager.load("ground")
                    else:
                        self.manager.load("run")
                        self.manager.annim_speed_factor = 1 + self.actual_speed*0.05
                elif (self.inertia.y < 1.5 or self.inertia.y > 0) and self.grounded:
                    if self.manager._loaded_name == "fall":
                        self.manager.load("ground")
                    else:
                        self.manager.load("idle")

            print(self.manager._loaded_name)

            #* walking particle here
            if self.grounded:
                self.double_jump = True
                if self.actual_speed > 1:
                    particle_group.add(Particule(10,Vector2(self.rect.left + self.image.get_width()//2,self.rect.bottom),self.image.get_width()//2,Vector2(-self.x_axis.value*2,0),0.25*self.actual_speed,True))

            #* CAMERA Update of the player
            x,y = CAMERA.to_virtual(INFO.current_w/2,INFO.current_h/2 )
            _x,_y = (self.rect.left,self.rect.top)
            CAMERA.x += (_x - x)*0.0001
            CAMERA.y += (_y - y)*0.0001
            #* Effect of dezoom relatif to speed
            zoom_target = 2.5*(1/(self.actual_speed*0.1 + 1))
            CAMERA.zoom += (zoom_target - CAMERA.zoom)*0.01
        
        if self.rect.top > map.water_level:
            self.rect.topleft = (100, 50)
        #* inertia and still update if inactive
        super().update(map,serialized)
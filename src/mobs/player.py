import pygame
from .MOTHER import MOB
from src.tools.tools import animation_Manager, sprite_sheet,Keyboard,Vector2
from src.tools.constant import TEAM,EndPartie,IMPACT,INTERACT,ENDTURN,DEATH,PATH
from src.game_effect.particule import Particule
from src.weapons.WEAPON import WEAPON

INFO = pygame.display.Info()

class Player(MOB):

    def __init__(self,name, pos, size,team,group, id_weapon):
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
        self.rigth_direction = True

        self.jump_force = 8
        self.double_jump = 0
        self.jump_cooldown = 0
        self.cooldown_double_jump = 400

        # for action
        self.lock = False
        self.weapon_manager = None # mettre travail de Joseph ici

        # pushback quand on collide un autre joueur
        self.cooldown_pushback=0.1
        self.timer_push_back=0
        self.load_team(team)

        self.current_weapon=WEAPON("sniper", self)

    @property
    def image(self) -> pygame.Surface:
        surf = self.manager.surface
        if self.rigth_direction:
            return surf
        else:
            return pygame.transform.flip(surf,True,False) #! if too much loss of perf we will stock both

    def load_team(self,team):
        idle = sprite_sheet(PATH / "assets" / "perso"/ team / "idle.png",TEAM[team]["idle"]) # load all annimation in annimation manager
        run = sprite_sheet(PATH / "assets" / "perso"/ team /  "run.png",TEAM[team]["run"]) 
        jump = sprite_sheet(PATH / "assets" / "perso"/ team /  "jump.png",TEAM[team]["jump"]) 
        fall = sprite_sheet(PATH / "assets" / "perso"/ team /  "fall.png",TEAM[team]["fall"]) 
        ground = sprite_sheet(PATH / "assets" / "perso"/ team /  "ground.png",TEAM[team]["ground"]) 
        emote = sprite_sheet(PATH / "assets" / "perso"/ team /  "emote.png",TEAM[team]["emote"]) 
        self.manager.add_annimation("idle",idle,10*TEAM[team]["speed_factor"])
        self.manager.add_annimation("run",run,10*TEAM[team]["speed_factor"])
        self.manager.add_annimation("jump",jump,10)
        self.manager.add_annimation("fall",fall,10)
        self.manager.add_annimation("ground",ground,15)
        self.manager.add_annimation("emote",emote,7)
        self.manager.add_link("jump","fall")
        self.manager.add_link("ground","idle")
        self.manager.add_link("emote","idle")
        self.manager.load("idle")

    def respawn(self,y):
        self.inertia.y = 0
        self.rect.y = y
        if not self.lock:
            pygame.event.post(pygame.event.Event(ENDTURN))

    def handle(self, event: pygame.event.Event):
        """methode appele a chaque event"""
        match event.type:
            case pygame.KEYUP if event.key == Keyboard.end_turn.key and not self.lock:
                pygame.event.post(pygame.event.Event(ENDTURN))
        super().handle(event)

    def update(self,map,players,serialized,CAMERA,particle_group):
        if not self.lock:
            self.x_axis.update(Keyboard.right.is_pressed,Keyboard.left.is_pressed)
            if Keyboard.jump.is_pressed:
                if self.jump_cooldown< pygame.time.get_ticks() and (self.grounded or self.double_jump):
                    self.double_jump = (self.inertia.y < 1 and self.inertia.y > 0) or self.grounded # this is like grounded but constant because sometime we are on the ground but not colliding because gravity too weak
                    self.inertia.y = -self.jump_force
                    self.grounded = False
                    self.jump_cooldown = pygame.time.get_ticks() + self.cooldown_double_jump
                    self.manager.load("jump")
                    for i in range(5):
                        particle_group.add(Particule(10,Vector2(self.rect.left + self.image.get_width()//2,self.rect.bottom),self.image.get_width()//2,Vector2(1,-2),2,pygame.Color(20,20,0)))
            if Keyboard.interact.is_pressed:
                #map.add_damage(Vector2(self.rect.left,self.rect.top),50)
                # ev = pygame.event.Event(INTERACT,{'rect':self.rect})
                # pygame.event.post(ev)
                # self.manager.load("emote")
                self.current_weapon.fire()
            if Keyboard.inventory.is_pressed:
                ...
            if Keyboard.up.is_pressed:
                self.current_weapon.aim("up")
            if Keyboard.down.is_pressed:
                self.current_weapon.aim("down")
            if Keyboard.pause.is_pressed:
                raise EndPartie
 
            if self.x_axis.value>0: # tempo variable so keep in cache until real changement of direction
                self.rigth_direction = True
            elif self.x_axis.value<0:
                self.rigth_direction = False

            #* walking particle here
            if self.grounded:
                self.double_jump = True
                if self.actual_speed > 1 and pygame.time.get_ticks()%7==0:
                    particle_group.add(Particule(10,Vector2(self.rect.left + self.image.get_width()//2,self.rect.bottom),self.image.get_width()//2,Vector2(-self.x_axis.value*2,0),0.25*self.actual_speed,pygame.Color(20,20,0)))

            #* CAMERA Update of the player
            x,y = CAMERA.to_virtual(INFO.current_w/2,INFO.current_h/2 )
            _x,_y = (self.rect.left,self.rect.top)
            CAMERA.x += (_x - x)*0.0001
            CAMERA.y += (_y - y)*0.0001
            #* Effect of dezoom relatif to speed
            zoom_target = 2.5*(1/(self.actual_speed*0.1 + 1))
            CAMERA.zoom += (zoom_target - CAMERA.zoom)*0.01
        else:
            self.x_axis.update()

        #* annimation
        if self.manager._loaded_name not in ["jump","ground","emote"]:
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
        # death
        if self.rect.bottom > map.water_level:
            ev = pygame.event.Event(DEATH,{"name":self.name,"pos":self.rect.bottomleft})
            pygame.event.post(ev)
        #* inertia and still update if inactive
        super().update(map,serialized,players)
        self.current_weapon.update(map,players)

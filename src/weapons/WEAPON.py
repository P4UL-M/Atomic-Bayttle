"""class mother des armes"""
import pygame
from src.game_effect.particule import Particule
from src.tools.constant import PATH, IMPACT
from src.tools.tools import Vector2,MixeurAudio
from src.weapons.physique import *
from src.mobs.MOTHER import MOB
from math import pi,cos,sin

class Bullet(MOB):
    def __init__(self, pos:tuple[int], size:tuple[int],path:str,impact_surface:pygame.Surface,radius,force:int,angle:int,right_direction:bool, group):
        super().__init__(pos, size, group)
        self.__image = pygame.transform.scale(pygame.image.load(path),size)
        self.image = self.__image.copy()
        self.real_rect = self.rect.copy()
        self.__image.convert_alpha()
        self.impact_surface = impact_surface
        
        self.right_direction = right_direction
        self.trajectoire = trajectoire(pos,angle,force)
        self.t0 = pygame.time.get_ticks()
        self.radius = radius
        self.name = f"bullet_{pygame.time.get_ticks()}"
        x = self.trajectoire.get_x(1)
        y = - self.trajectoire.get_y(1)
        _d = Vector2(x,y)
        self.image,self.rect = self.rot_center(_d.arg)

        self.speed = 1
        self.path_sound = PATH / "assets" / "sound" / "kill_sound.wav"
        self.damage = 20
        self.multiplicator_repulsion = 0.8

    def move(self,target,players,*arg,**kargs):
        try:
            self.__getattribute__("rect")
        except:
            raise AttributeError("MOB must have a rect to move")
        
        t = (pygame.time.get_ticks() - self.t0)/100 * self.speed
        x = self.trajectoire.get_x(t)
        y = - self.trajectoire.get_y(x) + self.trajectoire.pos0[1]
        if not self.right_direction:
            x *= -1
        x += self.trajectoire.pos0[0]
        _d = Vector2(x-self.real_rect.left,y-self.real_rect.top)
        self.actual_speed = _d.lenght

        _movements = [self.real_rect.width // 4 for i in range(int(self.actual_speed/(self.real_rect.width // 4)))] + [self.actual_speed%(self.real_rect.width // 4)]
        
        for i in _movements:
            if _d.arg != None: # arg is none we have no movement
                __d = _d.unity * i
                for player in players:
                    if player is not self and self.mask.collide(self.real_rect.topleft,player) and not "bullet" in player.name:
                        pygame.event.post(pygame.event.Event(IMPACT,{"x":self.real_rect.centerx,"y":self.real_rect.centery,"radius":self.radius,"multiplicator_repulsion":self.multiplicator_repulsion,"damage":self.damage}))
                        self.kill()
                        MixeurAudio.play_effect(self.path_sound)
                        return
                if self.mask.collide(self.real_rect.topleft,target):
                    pygame.event.post(pygame.event.Event(IMPACT,{"x":self.real_rect.centerx,"y":self.real_rect.centery,"radius":self.radius,"multiplicator_repulsion":self.multiplicator_repulsion,"damage":self.damage}))
                    self.kill()
                    MixeurAudio.play_effect(self.path_sound)
                    return
                self.real_rect.move_ip(*__d)
        
        self.image,self.rect = self.rot_center(_d.arg)

    def collide_reaction(self, *arg,**kargs):
        ...

    def update(self, map, players,*arg,**kargs):
        if not self.rect.colliderect(map.rect):
            self.kill()
        super().update(map,1, players)

    def rot_center(self, angle):
    
        rotated_image = pygame.transform.rotate(self.__image, -angle*180/pi)
        new_rect = rotated_image.get_rect(center = self.__image.get_rect(center = self.real_rect.topleft).center)

        return rotated_image, new_rect

class Grenade(Bullet):
    def __init__(self, pos: tuple[int], size: tuple[int], path: str, impact_surface: pygame.Surface, radius, force: int, angle: int, right_direction: bool, group):
        super().__init__(pos, size, path, impact_surface, radius, force, angle, right_direction, group)
        self.speed = 0.7
        self.path_sound = PATH / "assets" / "sound" / "grenade_sound.wav"
        self.multiplicator_repulsion = 1.2
        self.damage = 40

    def update(self, map, players, *arg, **kargs):
        super().update(map, players, *arg, **kargs)
        self.image, self.rect = self.rot_center(pygame.time.get_ticks()/100)

class WEAPON(pygame.sprite.Sprite): 
    def __init__(self,path):
        super().__init__()
        self.__image=pygame.image.load(path).convert_alpha()
        self.image = self.__image.copy()
        self.pivot = (self.__image.get_width()//3,self.__image.get_height()//2)
        self.real_rect = self.__image.get_rect(topleft=(0,0))
        self.rect = self.__image.get_rect(topleft = (self.real_rect.x-self.pivot[0], self.real_rect.y-self.pivot[1]))
        self.l = self.real_rect.width
        self.__cooldown = 0
        self.angle = 0

    def fire(self,right_direction,group,particle_group):
        if self.__cooldown + self.cooldown < pygame.time.get_ticks():
            self.__cooldown = pygame.time.get_ticks()
            angle = self.angle
            x = self.l*0.4 * cos(angle) * (1.5 if right_direction else -2.3) + self.real_rect.left
            y = -self.l * sin(angle) + self.real_rect.top
            Bullet((x,y),(14,7),self.bullet,pygame.Surface((5,3)),self.rayon,self.v0,angle,right_direction,group)
            for i in range(5):
                particle_group.add(Particule(2,Vector2(x,y),1,Vector2(x,y).unity*-1,5,pygame.Color(60,0,0),False,(2,2)))

    def update(self,pos,right,_dangle):
        self.angle += _dangle
        if self.angle > pi/2: self.angle = pi/2
        elif self.angle < -pi/2: self.angle = -pi/2
        self.real_rect.topleft =pos

        offset = self.pivot

        if not right:
            image = pygame.transform.flip(self.__image,True,False)
            offset = (self.__image.get_width()//3*2,self.__image.get_height()//2)
            angle = self.angle*-1
        else:
            image = self.__image.copy()
            angle = self.angle

        image_rect = image.get_rect(topleft = (self.real_rect.left-offset[0], self.real_rect.top-offset[1]))
        offset_center_to_pivot = pygame.math.Vector2(self.real_rect.topleft) - image_rect.center
        rotated_offset = offset_center_to_pivot.rotate(-angle*180/pi)
        rotated_image_center = (self.real_rect.left - rotated_offset.x, self.real_rect.top - rotated_offset.y)
        self.image = pygame.transform.rotate(image, angle*180/pi).convert_alpha()
        self.rect = self.image.get_rect(center = rotated_image_center)

class Sniper(WEAPON):
    def __init__(self) -> None:
        self.bullet=PATH/"assets"/"laser"/"14.png"
        self.v0=100
        self.rayon=30
        self.cooldown = 100
        super().__init__(PATH/"assets"/"weapons"/"sniper.png")

class Launcher(WEAPON):
    def __init__(self) -> None:
        self.bullet=PATH/"assets"/"laser"/"grenade.png"
        self.v0=50
        self.rayon=50
        self.cooldown = 500
        self.__cooldown = 0
        super().__init__(PATH/"assets"/"weapons"/"launcher.png")

    def fire(self, right_direction, group, particle_group):
        if self.__cooldown + self.cooldown < pygame.time.get_ticks():
            self.__cooldown = pygame.time.get_ticks()
            angle = self.angle
            x = self.l*0.4 * cos(angle) * (1.5 if right_direction else -2.3) + self.real_rect.left
            y = -self.l * sin(angle) + self.real_rect.top
            Grenade((x,y),(14,7),self.bullet,pygame.Surface((5,3)),self.rayon,self.v0,angle,right_direction,group)
            MixeurAudio.play_effect(PATH / "assets" / "sound" / "rocket_launch.wav",0.5)
            for i in range(5):
                particle_group.add(Particule(2,Vector2(x,y),1,Vector2(x,y).unity*-1,5,pygame.Color(60,0,0),False,(2,2)))
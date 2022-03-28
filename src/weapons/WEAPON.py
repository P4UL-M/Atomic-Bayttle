"""class mother des armes"""
import pygame
from src.game_effect.particule import Particule, AnimatedParticule
from src.tools.constant import PATH, IMPACT
import src.tools.constant as tl
from src.tools.tools import Vector2, MixeurAudio, Keyboard, sprite_sheet
from src.weapons.physique import *
from src.mobs.MOTHER import MOB
from math import pi, cos, sin

_list_weapon = []


def add_weapon(_class):
    global _list_weapon
    _list_weapon.append(_class)
    return _class


class Bullet(MOB):
    def __init__(self, pos: tuple[int], size: tuple[int], path: str, impact_surface: pygame.Surface, radius, force: int, angle: int, right_direction: bool, group):
        super().__init__(pos, size, group)
        self.real_image = pygame.transform.scale(pygame.image.load(path), size)
        self.image = self.real_image.copy()
        self.real_rect = self.rect.copy()
        self.real_image.convert_alpha()
        self.impact_surface = impact_surface

        self.right_direction = right_direction
        self.trajectoire = trajectoire(pos, angle, force)
        self.t0 = pygame.time.get_ticks()
        self.radius = radius
        self.name = f"bullet_{pygame.time.get_ticks()}"
        _d = Vector2(self.trajectoire.get_x(1)-self.trajectoire.get_x(0),
                     self.trajectoire.get_y(1) - self.trajectoire.get_y(0))
        self.image, self.rect = self.rot_center(_d.arg)

        self.speed = 1
        self.path_sound = PATH / "assets" / "sound" / "kill_sound.wav"
        self.damage = 20
        self.multiplicator_repulsion = 0.8

        self.particle_sprite = sprite_sheet(
            PATH/"assets"/"explosion"/"explosion-6.png", (48, 48))
        self.size_particule = 0.3
        self.particle_sprite.config(
            (self.radius*2*self.size_particule, self.radius*2*self.size_particule))

    def move(self, GAME, CAMERA):
        GM = GAME.partie
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
        _d = Vector2(x-self.real_rect.left, y-self.real_rect.top)
        self.actual_speed = _d.lenght

        _movements = [self.real_rect.width // 4 for i in range(int(self.actual_speed/(
            self.real_rect.width // 4)))] + [self.actual_speed % (self.real_rect.width // 4)]

        for i in _movements:
            if _d.arg != None:  # arg is none we have no movement
                __d = _d.unity * i
                for player in GM.players:
                    if player is not self and self.mask.collide(self.real_rect.topleft, player) and not "bullet" in player.name:
                        pygame.event.post(pygame.event.Event(IMPACT, {"x": self.real_rect.centerx, "y": self.real_rect.centery, "radius": self.radius, "multiplicator_repulsion": self.multiplicator_repulsion, "damage": self.damage, "particle": AnimatedParticule(
                            self.particle_sprite, 7, Vector2(self.real_rect.centerx - self.radius*self.size_particule, self.real_rect.centery - self.radius*self.size_particule), 1, Vector2(0, 0), 0, False)}))
                        self.kill()
                        MixeurAudio.play_effect(self.path_sound)
                        return
                if self.mask.collide(self.real_rect.topleft, GM.map):
                    pygame.event.post(pygame.event.Event(IMPACT, {"x": self.real_rect.centerx, "y": self.real_rect.centery, "radius": self.radius, "multiplicator_repulsion": self.multiplicator_repulsion, "damage": self.damage, "particle": AnimatedParticule(
                        self.particle_sprite, 7, Vector2(self.real_rect.centerx - self.radius*self.size_particule, self.real_rect.centery - self.radius*self.size_particule), 1, Vector2(0, 0), 0, False)}))
                    self.kill()
                    MixeurAudio.play_effect(self.path_sound)
                    return
                self.real_rect.move_ip(*__d)

        self.image, self.rect = self.rot_center(_d.arg)
        return _d.unity

    def collide_reaction(self, *arg, **kargs):
        ...

    def handle(self, event: pygame.event.Event, *args, **kargs): ...

    def update(self, GAME, CAMERA):
        GM = GAME.partie
        if not self.rect.colliderect(GM.map.rect):
            self.kill()
        return super().update(GAME, CAMERA)

    def rot_center(self, angle):

        rotated_image = pygame.transform.rotate(
            self.real_image, -(angle or 0)*180/pi)
        new_rect = rotated_image.get_rect(
            center=self.real_image.get_rect(center=self.real_rect.topleft).center)

        return rotated_image, new_rect


class Grenade(Bullet):
    def __init__(self, pos: tuple[int], size: tuple[int], path: str, impact_surface: pygame.Surface, radius, force: int, speed: int, angle: int, right_direction: bool, group):
        super().__init__(pos, size, path, impact_surface,
                         radius, force, angle, right_direction, group)
        self.speed = speed * 0.7
        self.path_sound = PATH / "assets" / "sound" / "grenade_sound.wav"
        self.multiplicator_repulsion = 1.2
        self.damage = 40

        self.particle_sprite = sprite_sheet(
            PATH/"assets"/"explosion"/"explosion-1.png", (32, 32))
        self.size_particule = 0.8
        self.particle_sprite.config(
            (self.radius*2*self.size_particule, self.radius*2*self.size_particule))

    def update(self, GAME, CAMERA):
        _d = super().update(GAME, CAMERA)
        _d = (_d if _d else Vector2(1, 1)) * -1
        GAME.partie.group_particle.add(Particule(4, Vector2(
            *self.real_rect.center), 1, _d, 2, pygame.Color(0, 0, 0), gravity=True, size=(2, 2)))
        self.image, self.rect = self.rot_center(pygame.time.get_ticks()/100)


class WEAPON(pygame.sprite.Sprite):
    def __init__(self, path):
        super().__init__()
        self.real_image = pygame.image.load(path).convert_alpha()
        self.image = self.real_image.copy()
        self.pivot = (1/3, 1/2)
        self.real_rect = self.real_image.get_rect(topleft=(0, 0))
        self.rect = self.real_image.get_rect(
            topleft=(self.real_rect.x-self.pivot[0], self.real_rect.y-self.pivot[1]))
        self.l = self.real_rect.width
        self.__cooldown = 0
        self.angle = 0

        self.lock = False

    def handle(self, event: pygame.event.Event, owner, GAME, CAMERA):
        """methode appele a chaque event"""
        match event.type:
            case tl.CHARGING:
                if self.__cooldown + self.cooldown < pygame.time.get_ticks() and event.weapon == self:
                    self.__cooldown = pygame.time.get_ticks()
                    self.fire(owner.right_direction, GAME.partie.mobs, GAME.partie.group_particle,
                              force=self.v0 * event.value, speed=event.value*0.3 + 0.9)
                    self.lock = False

    def fire(self, right_direction, group, particle_group, force=None, speed: int = 1):
        angle = self.angle
        x = self.l*0.4 * \
            cos(angle) * (1.5 if right_direction else -2.3) + self.real_rect.left
        y = -self.l * sin(angle) + self.real_rect.top
        Bullet((x, y), (14, 7), self.bullet, pygame.Surface((5, 3)),
               self.rayon, self.v0, angle, right_direction, group)
        for i in range(5):
            particle_group.add(Particule(2, Vector2(x, y), 1, Vector2(
                x, y).unity*-1, 5, pygame.Color(60, 0, 0), False, (2, 2)))

    def update(self, pos: tuple, right: bool, _dangle: int, lock=False):
        self.angle += _dangle
        if self.angle > pi/2:
            self.angle = pi/2
        elif self.angle < -pi/2:
            self.angle = -pi/2
        self.real_rect.topleft = pos

        offset = (int(self.real_image.get_width() *
                      self.pivot[0]), int(self.real_image.get_height()*self.pivot[1]))

        if not right:
            image = pygame.transform.flip(self.real_image, True, False)
            offset = (int(image.get_width() * (1 -
                                               self.pivot[0])), int(image.get_height()*self.pivot[1]))
            angle = self.angle*-1
        else:
            image = self.real_image.copy()
            angle = self.angle

        image_rect = image.get_rect(
            topleft=(self.real_rect.left-offset[0], self.real_rect.top-offset[1]))
        offset_center_to_pivot = pygame.math.Vector2(
            self.real_rect.topleft) - image_rect.center
        rotated_offset = offset_center_to_pivot.rotate(-angle*180/pi)
        rotated_image_center = (
            self.real_rect.left - rotated_offset.x, self.real_rect.top - rotated_offset.y)
        self.image = pygame.transform.rotate(
            image, angle*180/pi).convert_alpha()
        self.rect = self.image.get_rect(center=rotated_image_center)

    def clean(self):
        ...


@ add_weapon
class Sniper(WEAPON):
    def __init__(self) -> None:
        self.bullet = PATH/"assets"/"laser"/"14.png"
        self.v0 = 100
        self.rayon = 30
        self.cooldown = 100
        super().__init__(PATH/"assets"/"weapons"/"sniper.png")


@ add_weapon
class Launcher(WEAPON):
    def __init__(self) -> None:
        self.bullet = PATH/"assets"/"laser"/"grenade.png"
        self.v0 = 50
        self.rayon = 50
        self.cooldown = 500
        self.__cooldown = 0
        super().__init__(PATH/"assets"/"weapons"/"launcher.png")
        self.pivot = (1/2, 1/2)

    def handle(self, event: pygame.event.Event, owner, GAME, CAMERA):
        """methode appele a chaque event"""
        match event.type:
            case tl.CHARGING:
                if self.__cooldown + self.cooldown < pygame.time.get_ticks() and event.weapon == self:
                    if Keyboard.interact.is_pressed and event.value <= 1:
                        if owner.weapon_manager.zoom_factor > 0.5:
                            owner.weapon_manager.zoom_factor -= 0.2
                        pygame.event.post(pygame.event.Event(
                            tl.CHARGING, {"weapon": self, "value": event.value + 0.032}))
                        self.lock = True
                    else:
                        owner.weapon_manager.zoom_factor = 1
                        self.__cooldown = pygame.time.get_ticks()
                        self.fire(owner.right_direction, GAME.partie.mobs, GAME.partie.group_particle,
                                  force=self.v0 * event.value, speed=event.value*0.3 + 0.9)
                        self.lock = False

    def fire(self, right_direction, group, particle_group, force=None, speed: int = 1):
        angle = self.angle
        x = self.l*0.4 * \
            cos(angle) * (1.5 if right_direction else -2.3) + self.real_rect.left
        y = -self.l * sin(angle) + self.real_rect.top
        Grenade((x, y), (14, 7), self.bullet, pygame.Surface(
            (5, 3)), self.rayon, force or self.v0, speed, angle, right_direction, group)
        MixeurAudio.play_effect(
            PATH / "assets" / "sound" / "rocket_launch.wav", 0.5)
        for i in range(5):
            particle_group.add(Particule(2, Vector2(x, y), 1, Vector2(
                x, y).unity*-1, 5, pygame.Color(60, 0, 0), False, (2, 2)))


@ add_weapon
class Chainsaw(WEAPON):
    def __init__(self) -> None:
        self.rayon = 35
        self.damage = 15
        self.multiplicator_repulsion = 0.2
        self.cooldown = 100
        self.__cooldown = 0
        self.sound_cooldown = 1000
        self.__sound_cooldown = 0
        self.idle_sound = None
        super().__init__(PATH/"assets"/"weapons"/"chainsaw.png")
        self.pivot = (1/5, 1/2)

    def handle(self, event: pygame.event.Event, owner, GAME, CAMERA):
        """methode appele a chaque event"""
        match event.type:
            case tl.CHARGING:
                if self.__cooldown + self.cooldown < pygame.time.get_ticks() and event.weapon == self:
                    self.__cooldown = pygame.time.get_ticks()
                    self.fire(owner.right_direction, GAME.partie.mobs,
                              GAME.partie.group_particle)
                    self.lock = False

    def fire(self, right_direction, group, particle_group):
        angle = self.angle
        x = self.l*0.4 * \
            cos(angle) * (1.5 if right_direction else -2.3) + self.real_rect.left
        y = -self.l * sin(angle) + self.real_rect.top
        pygame.event.post(pygame.event.Event(IMPACT, {
                          "x": x, "y": y, "radius": self.rayon, "multiplicator_repulsion": self.multiplicator_repulsion, "damage": self.damage, "particle": None}))
        if self.__sound_cooldown + self.sound_cooldown < pygame.time.get_ticks():
            self.__sound_cooldown = pygame.time.get_ticks()
            if self.idle_sound:
                self.idle_sound()
            self.idle_sound = MixeurAudio.play_effect(
                PATH / "assets" / "sound" / "chainsaw_hit.wav", 0.5)
        for i in range(5):
            particle_group.add(Particule(2, Vector2(x, y), 1, Vector2(
                x, y).unity*-1, 5, pygame.Color(60, 0, 0), False, (2, 2)))

    def update(self, pos, right, _dangle, lock):
        super().update(pos, right, _dangle)
        if not lock:
            if not self.idle_sound:
                self.idle_sound = MixeurAudio.play_until_Stop(
                    PATH / "assets" / "sound" / "chainsaw_idle.wav", 1.2)
        else:
            if self.idle_sound:
                self.idle_sound()
                self.idle_sound = None

    def clean(self):
        self.idle_sound()
        self.idle_sound = None

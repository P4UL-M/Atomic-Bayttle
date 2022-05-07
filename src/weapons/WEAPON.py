from __future__ import annotations
import pygame
from src.game_effect.particule import Particule, AnimatedParticule
from src.tools.constant import PATH, IMPACT, TEAM
import src.tools.constant as tl
from src.tools.tools import Vector2, MixeurAudio, Keyboard, sprite_sheet
from src.weapons.physique import *
from src.mobs.MOTHER import MOB
from math import pi, cos, sin
import random

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game import *
    from src.mobs.player import Player

_list_weapon = []


def add_weapon(_class):
    _list_weapon.append(_class)
    return _class


class Bullet(MOB):
    def __init__(self, pos: tuple[int], size: tuple[int], path: str, impact_surface: pygame.Surface, radius, force: int, angle: int, right_direction: bool, group):
        super().__init__(pos, size, group)
        self.real_image = pygame.transform.scale(pygame.image.load(path), size)
        self.rect = self.real_image.get_rect(center=pos)
        self.image = self.real_image.copy()
        self.real_rect = self.rect.copy()
        self.real_image.convert_alpha()
        self.impact_surface = impact_surface

        self.right_direction = right_direction
        self.trajectoire = trajectoire(pos, angle, force)
        self.t0 = pygame.time.get_ticks()
        self.radius = radius
        self.name = f"bullet_{pygame.time.get_ticks()}"
        _d = Vector2(self.trajectoire.get_x(1) - self.trajectoire.get_x(0), self.trajectoire.get_y(1) - self.trajectoire.get_y(0))
        self.image, self.rect = self.rot_center(_d.arg)

        self.speed = 1
        self.path_sound = PATH / "assets" / "sound" / "kill_sound.wav"
        self.damage = 4
        self.multiplicator_repulsion = 0.6
        self.friendly_fire = False

        self.particle_sprite = sprite_sheet(
            PATH / "assets" / "explosion" / "explosion-6.png", (48, 48))
        self.size_particule = 0.9
        self.particle_sprite.config(
            (self.radius * 2 * self.size_particule, self.radius * 2 * self.size_particule))

    def move(self, GAME, CAMERA):
        GM = GAME.partie
        try:
            self.__getattribute__("rect")
        except:
            raise AttributeError("MOB must have a rect to move")

        t = (pygame.time.get_ticks() - self.t0) / 100 * self.speed
        x = self.trajectoire.get_x(t)
        y = - self.trajectoire.get_y(x) + self.trajectoire.pos0[1]
        if not self.right_direction:
            x *= -1
        x += self.trajectoire.pos0[0]
        _d = Vector2(x - self.real_rect.left, y - self.real_rect.top)
        self.actual_speed = _d.lenght

        _movements = [self.real_rect.width // 4 for i in range(int(self.actual_speed / (
            self.real_rect.width // 4)))] + [self.actual_speed % (self.real_rect.width // 4)]

        for i in _movements:
            if _d.arg is not None:  # arg is none we have no movement
                __d = _d.unity * i
                for player in GM.players:
                    if player is not self and self.mask.collide(self.real_rect.topleft, player) and not "bullet" in player.name:
                        if player.lock or t > 5:
                            x, y = self.mask.collide(self.real_rect.topleft, player, True)
                            pygame.event.post(pygame.event.Event(IMPACT, {"x": self.real_rect.left + x, "y": self.real_rect.top + y, "radius": self.radius, "multiplicator_repulsion": self.multiplicator_repulsion, "damage": self.damage, "friendly_fire": self.friendly_fire, "player_cancel": False}))
                            GM.group_particle.add(AnimatedParticule(self.particle_sprite, 7, Vector2(self.real_rect.centerx - self.radius * self.size_particule, self.real_rect.centery - self.radius * self.size_particule), 1, Vector2(0, 0), 0, False))
                            self.kill()
                            MixeurAudio.play_effect(self.path_sound)
                            return
                if self.mask.collide(self.real_rect.topleft, GM.map):
                    x, y = self.mask.collide(self.real_rect.topleft, GM.map, True)
                    pygame.event.post(pygame.event.Event(IMPACT, {"x": self.real_rect.left + x, "y": self.real_rect.top + y, "radius": self.radius, "multiplicator_repulsion": self.multiplicator_repulsion, "damage": self.damage, "friendly_fire": self.friendly_fire, "player_cancel": False}))
                    GM.group_particle.add(AnimatedParticule(self.particle_sprite, 7, Vector2(self.real_rect.centerx - self.radius * self.size_particule, self.real_rect.centery - self.radius * self.size_particule), 1, Vector2(0, 0), 0, False))
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
        if (self.rect.y > 0 and not self.rect.colliderect(GM.map.rect)) or self.rect.y < -GM.map.rect.height * 0.3:
            self.kill()
        return super().update(GAME, CAMERA)

    def rot_center(self, angle):

        rotated_image = pygame.transform.rotate(
            self.real_image, -(angle or 0) * 180 / pi)
        new_rect = rotated_image.get_rect(
            center=self.real_image.get_rect(center=self.real_rect.topleft).center)

        return rotated_image, new_rect


class Grenade(Bullet):
    def __init__(self, pos: tuple[int], size: tuple[int], path: str, impact_surface: pygame.Surface, radius, force: int, repulsion: int, speed: int, angle: int, right_direction: bool, group):
        super().__init__(pos, size, path, impact_surface, radius, force, angle, right_direction, group)
        self.speed = speed * 0.7
        self.path_sound = PATH / "assets" / "sound" / "grenade_sound.wav"
        self.multiplicator_repulsion = repulsion
        self.damage = 40
        self.friendly_fire = True

        self.particle_sprite = sprite_sheet(
            PATH / "assets" / "explosion" / "explosion-1.png", (32, 32))
        self.size_particule = 0.8
        self.particle_sprite.config(
            (self.radius * 2 * self.size_particule, self.radius * 2 * self.size_particule))

    def update(self, GAME, CAMERA):
        _d = super().update(GAME, CAMERA)
        _d = (_d if _d else Vector2(1, 1)) * -1
        GAME.partie.group_particle.add(Particule(4, Vector2(*self.real_rect.center), 1, _d, 2, pygame.Color(0, 0, 0), gravity=True, size=(2, 2)))
        self.image, self.rect = self.rot_center(pygame.time.get_ticks() / 100)


class WEAPON(pygame.sprite.Sprite):
    def __init__(self, path, img_name):
        super().__init__()
        self.visible = True
        self.real_image = pygame.image.load(path / img_name).convert_alpha()
        self.icon = pygame.image.load(path / 'icon.png').convert_alpha()
        transColor = self.icon.get_at((0, 0))
        self.icon.set_colorkey(transColor)
        self.image = self.real_image.copy()
        self.pivot = (1 / 3, 1 / 2)
        self.end = (1.2, 1 / 2)
        self.end_offset = ()
        self.real_rect = self.real_image.get_rect(topleft=(0, 0))
        self.rect = self.real_image.get_rect(topleft=(self.real_rect.x - self.pivot[0], self.real_rect.y - self.pivot[1]))
        self.l = self.real_rect.width
        self.__cooldown = 0
        self.magazine = 0
        self.angle = 0
        self.angle_spread = 0.005 * pi

        self.lock = False

    def handle(self, event: pygame.event.Event, owner, GAME, CAMERA):
        """methode appele a chaque event"""
        match event.type:
            case tl.CHARGING:
                if self.__cooldown + self.cooldown < pygame.time.get_ticks() and event.weapon == self:
                    self.__cooldown = pygame.time.get_ticks()
                    self.fire(owner, GAME.partie.mobs, GAME.partie.group_particle, force=self.v0 * event.value, speed=event.value * 0.3 + 0.9)
                    self.lock = False

    def fire(self, owner: Player, group, particle_group, force=None, speed: int = 1):
        angle = self.angle + random.uniform(-self.angle_spread, self.angle_spread)
        x = self.end_offset[0] * (1 + owner.actual_speed / 40) + owner.rect.centerx
        y = self.end_offset[1] * (1 + owner.actual_speed / 40) + owner.rect.centery
        Bullet((x, y), (14, 7), self.bullet, pygame.Surface((5, 3)), self.rayon, self.v0, angle, owner.right_direction, group)
        self.magazine -= 1
        if self.magazine <= 0:
            ev = pygame.event.Event(tl.ENDTURN)
            pygame.event.post(ev)
        for i in range(5):
            particle_group.add(Particule(2, Vector2(x, y), 1, Vector2(x, y).unity * -1, 5, pygame.Color(60, 0, 0), False, (2, 2)))

    def reload(self):
        ...

    def update(self, pos: tuple, right: bool, angle: int, lock, CAMERA: Camera):
        self.angle = angle
        self.real_rect.topleft = pos

        offset = (int(self.real_image.get_width() * self.pivot[0]), int(self.real_image.get_height() * self.pivot[1]))
        end = (int(self.real_image.get_width() * self.end[0]), int(self.real_image.get_height() * self.end[1]))

        if not right:
            image = pygame.transform.flip(self.real_image, True, False)
            offset = (int(image.get_width() * (1 - self.pivot[0])), int(image.get_height() * self.pivot[1]))
            end = (int(image.get_width() * (1 - self.end[0])), int(image.get_height() * self.end[1]))
            angle = self.angle * -1
        else:
            image = self.real_image.copy()
            angle = self.angle

        # calcul postion with offset center of rotation
        image_rect = image.get_rect(topleft=(self.real_rect.left - offset[0], self.real_rect.top - offset[1]))
        offset_center_to_pivot = pygame.math.Vector2(self.real_rect.topleft) - image_rect.center
        rotated_offset = offset_center_to_pivot.rotate(-angle * 180 / pi)
        rotated_image_center = (self.real_rect.left - rotated_offset.x, self.real_rect.top - rotated_offset.y)
        self.image = pygame.transform.rotate(image, angle * 180 / pi).convert_alpha()
        self.rect = self.image.get_rect(center=rotated_image_center)

        # calcul end posision
        image_rect_end = image.get_rect(topleft=(self.real_rect.left - end[0], self.real_rect.top - end[1]))
        offset_center_to_end = pygame.math.Vector2(self.real_rect.topleft) - image_rect_end.center
        self.end_offset = offset_center_to_end.rotate(-angle * 180 / pi)

        if self.visible:
            self.drawUI(CAMERA)

    def clean(self):
        ...

    def drawUI(self, CAMERA):
        ...


@ add_weapon
class Auto(WEAPON):
    def __init__(self, team) -> None:
        self.bullet = PATH / "assets" / "laser" / "14.png"
        self.v0 = 100
        self.rayon = 5
        self.cooldown = 12
        self.magazine_max = 16
        self.path = PATH / "assets" / "perso" / team / "weapon" / 'auto'
        super().__init__(self.path, "auto.png")
        self.pivot = TEAM[team]["auto_pivot"]
        self.bullet_UI = sprite_sheet(PATH / "assets" / "weapons" / "UI" / "red_bullet.png", (24, 24))
        self.bullet_UI.config((24 * 2, 24 * 2))

    def reload(self):
        self.magazine = self.magazine_max

    def drawUI(self, CAMERA):
        for i in range(min(self.magazine, 7)):
            _bullet: pygame.Surface = self.bullet_UI[pygame.time.get_ticks() // 100 + i]
            CAMERA._screen_UI.blit(_bullet, (_bullet.get_width() * i + 4 * i + 3, CAMERA._screen_UI.get_height() - _bullet.get_height() - 3))

    def update(self, pos: tuple, right: bool, angle: int, lock, CAMERA):
        if self.magazine < 1:
            self.real_image = pygame.image.load(self.path / "auto_alternate.png").convert_alpha()
        else:
            self.real_image = pygame.image.load(self.path / "auto.png").convert_alpha()
        return super().update(pos, right, angle, lock, CAMERA)


@ add_weapon
class Launcher(WEAPON):
    def __init__(self, team) -> None:
        self.bullet = PATH / "assets" / "laser" / "grenade.png"
        self.v0 = 50
        self.rayon = 50
        self.cooldown = 500
        self.__cooldown = 0
        self.path = PATH / "assets" / "perso" / team / "weapon" / "launcher"
        super().__init__(self.path, "launcher.png")
        self.pivot = TEAM[team]["launcher_pivot"]
        self.magazine_max = 1

        self.chargingsound = None
        self.factor = 0.1

        self.slider = pygame.image.load(PATH / "assets" / "weapons" / "UI" / "force.png").convert()
        self.slider = pygame.transform.scale(self.slider, (int(self.slider.get_width() * 2), int(self.slider.get_height() * 2)))
        self.bar = pygame.image.load(PATH / "assets" / "weapons" / "UI" / "ForceBar.png").convert_alpha()
        self.bar = pygame.transform.scale(self.bar, (int(self.bar.get_width() * 2), int(self.bar.get_height() * 2)))

    def handle(self, event: pygame.event.Event, owner, GAME, CAMERA):
        """methode appele a chaque event"""
        match event.type:
            case tl.CHARGING:
                if self.__cooldown + self.cooldown < pygame.time.get_ticks() and event.weapon == self:
                    if Keyboard.interact.is_pressed and event.value <= 2 and not owner.lock:
                        if owner.weapon_manager.zoom_factor > 0.5:
                            owner.weapon_manager.zoom_factor -= 0.2
                        pygame.event.post(pygame.event.Event(tl.CHARGING, {"weapon": self, "value": event.value + 0.032 * GAME.serialized}))
                        self.lock = True
                        self.factor = event.value + 0.032 * GAME.serialized
                        if not self.chargingsound:
                            self.chargingsound = MixeurAudio.play_until_Stop(
                                PATH / "assets" / "sound" / "weapon_charge.wav", volume=2)
                    else:
                        owner.weapon_manager.zoom_factor = 1
                        self.__cooldown = pygame.time.get_ticks()
                        self.fire(owner, GAME.partie.mobs, GAME.partie.group_particle, force=self.v0 * event.value, speed=event.value * 0.3 + 0.9)
                        self.lock = False
                        self.magazine -= 1
                        if self.magazine <= 0:
                            pygame.event.post(pygame.event.Event(tl.ENDTURN, {"player": owner}))
                        if self.chargingsound:
                            self.chargingsound()
                            self.chargingsound = None

    def fire(self, owner: Player, group, particle_group, force=None, speed: int = 1):
        angle = self.angle
        x = self.l * 0.4 * cos(angle) * (1.5 if owner.right_direction else -2.3) + self.real_rect.left
        y = -self.l * sin(angle) + self.real_rect.top
        rayon = self.rayon * min(max(force / self.v0, 1), 1.4)
        Grenade((x, y), (14, 7), self.bullet, pygame.Surface((5, 3)), rayon, force or self.v0, 1.2 * max(force / self.v0, 1), speed, angle, owner.right_direction, group)
        MixeurAudio.play_effect(PATH / "assets" / "sound" / "rocket_launch.wav", 0.5)
        for i in range(5):
            particle_group.add(Particule(2, Vector2(x, y), 1, Vector2(
                x, y).unity * -1, 5, pygame.Color(60, 0, 0), False, (2, 2)))

    def reload(self):
        self.magazine = self.magazine_max
        self.factor = 0.1

    def drawUI(self, CAMERA):
        slider = self.slider.copy()
        slider = pygame.transform.scale(slider, (int(self.bar.get_width() * (self.factor / 2) * 0.75), slider.get_height()))
        CAMERA._screen_UI.blit(self.bar, (10, CAMERA._screen_UI.get_height() - self.bar.get_height() - 10))
        CAMERA._screen_UI.blit(slider, (10 + 32, CAMERA._screen_UI.get_height() - 20 - 10))

    def update(self, pos: tuple, right: bool, angle: int, lock, CAMERA):
        if self.magazine == 0:
            self.real_image = pygame.image.load(self.path / "launcher_alternate.png").convert_alpha()
        else:
            self.real_image = pygame.image.load(self.path / "launcher.png").convert_alpha()
        return super().update(pos, right, angle, lock, CAMERA)


@ add_weapon
class Chainsaw(WEAPON):
    def __init__(self, team) -> None:
        self.rayon = 35
        self.damage = 2
        self.multiplicator_repulsion = 0.25
        self.cooldown = 100
        self.__cooldown = 0
        self.sound_cooldown = 1000
        self.__sound_cooldown = 0
        self.idle_sound = None
        self.path = PATH / "assets" / "perso" / team / "weapon" / "chainsaw"
        super().__init__(self.path, "chainsaw.png")
        self.pivot = TEAM[team]["melee_pivot"]
        self.end = (1.3, 1 / 2)
        self.magazine_max = 15

        self.slider = pygame.image.load(PATH / "assets" / "weapons" / "UI" / "energy.png").convert_alpha()
        self.slider = pygame.transform.scale(self.slider, (int(self.slider.get_width() * 2), int(self.slider.get_height() * 2)))
        self.bar = pygame.image.load(PATH / "assets" / "weapons" / "UI" / "EnergyBar.png").convert_alpha()
        self.bar = pygame.transform.scale(self.bar, (int(self.bar.get_width() * 2), int(self.bar.get_height() * 2)))

    def handle(self, event: pygame.event.Event, owner, GAME: Game, CAMERA: Camera):
        """methode appele a chaque event"""
        match event.type:
            case tl.CHARGING:
                if self.__cooldown + self.cooldown < pygame.time.get_ticks() and event.weapon == self:
                    self.__cooldown = pygame.time.get_ticks()
                    self.fire(owner, GAME.partie.mobs, GAME.partie.group_particle)
                    self.magazine -= 1
                    if self.magazine <= 0:
                        pygame.event.post(pygame.event.Event(tl.ENDTURN, {"player": owner}))
                    self.lock = False

    def fire(self, owner: Player, group, particle_group):
        angle = self.angle
        x = self.l * 0.4 * cos(angle) * (1.5 if owner.right_direction else -2.3) + self.real_rect.left
        y = -self.l * sin(angle) + self.real_rect.top
        pygame.event.post(pygame.event.Event(IMPACT, {"x": x, "y": y, "radius": self.rayon, "multiplicator_repulsion": self.multiplicator_repulsion, "damage": self.damage, "friendly_fire": False, "player_cancel": True}))
        if self.__sound_cooldown + self.sound_cooldown < pygame.time.get_ticks():
            self.__sound_cooldown = pygame.time.get_ticks()
            if self.idle_sound:
                self.idle_sound()
            self.idle_sound = MixeurAudio.play_effect(self.path / "hit_melee.wav", 0.5)
        for i in range(5):
            particle_group.add(Particule(2, Vector2(x, y), 1, Vector2(x, y).unity * -1, 5, pygame.Color(0, 0, 0), False, (4, 4)))

    def update(self, pos, right, angle, lock, CAMERA):
        super().update(pos, right, angle, lock, CAMERA)
        if self.magazine == 0:
            self.real_image = pygame.image.load(self.path / "chainsaw_alternate.png").convert_alpha()
        else:
            self.real_image = pygame.image.load(self.path / "chainsaw.png").convert_alpha()

        if not lock:
            if not self.idle_sound:
                self.idle_sound = MixeurAudio.play_until_Stop(self.path / "idle_melee.wav", 1.2)
        else:
            if self.idle_sound:
                self.idle_sound()
                self.idle_sound = None

    def clean(self):
        if self.idle_sound:
            self.idle_sound()
        self.idle_sound = None

    def reload(self):
        self.magazine = self.magazine_max

    def drawUI(self, CAMERA: Camera):
        slider = self.slider.copy()
        slider = pygame.transform.scale(slider, (int(self.bar.get_width() * (self.magazine / self.magazine_max) * 0.765), slider.get_height()))
        CAMERA._screen_UI.blit(self.bar, (10, CAMERA._screen_UI.get_height() - self.bar.get_height() - 10))
        CAMERA._screen_UI.blit(slider, (10 + 30, CAMERA._screen_UI.get_height() - 16 - 10))

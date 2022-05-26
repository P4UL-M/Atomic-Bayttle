"""
Atomic Bay'ttle
Paul Mairesse, Axel Loones, Louis Le Meilleur, Joseph Bénard, Théo de Aranjo
This file contains main classes for all characters
"""
from __future__ import annotations
import pygame
from math import ceil, pi, sin, cos
from src.tools.tools import Vector2, Axis
import src.tools.constant as tl
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game import *
    from src.mobs.player import Player


class BodyPartSprite(pygame.mask.Mask):
    def __init__(self, pos: tuple, size: tuple):
        super().__init__(size, True)
        self.pos = Vector2(*[ceil(i) for i in pos])

    def collide(self, pos: tuple, target: pygame.sprite.Sprite, coord=False) -> bool:
        try:
            target.__getattribute__("rect")
        except:
            raise AttributeError("target must have a mask to detect collision")

        x_off = target.rect.left - (pos[0] + self.pos.x)
        y_off = target.rect.top - (pos[1] + self.pos.y)
        if coord:
            return self.overlap(target.mask, (x_off, y_off))
        return self.overlap(target.mask, (x_off, y_off)) is not None

    def collide_normal(self, pos: tuple, target: pygame.sprite.Sprite) -> Vector2:
        x = target.rect.left - (pos[0] + self.pos.x)
        y = target.rect.top - (pos[1] + self.pos.y)
        dx = self.overlap_area(target.mask, (x + 1, y)) - \
            self.overlap_area(target.mask, (x - 1, y))
        dy = self.overlap_area(target.mask, (x, y + 1)) - \
            self.overlap_area(target.mask, (x, y - 1))
        return Vector2(dx, dy)


class MOB(pygame.sprite.Sprite):

    def __init__(self, pos, size, group):
        super().__init__(group)
        self.visible = True
        self.phatom = False

        self.rect = pygame.Rect(*pos, *size)
        self.inertia = Vector2(0, 0)

        self.x_axis = Axis()
        self.y_axis = Axis()

        self.speed = 5
        self.actual_speed = 0
        self.gravity = 0.05
        self.life_multiplicator = 0

        self.grounded = False  # vérification si au sol ou non

        # body part with position relative to the player position
        self.body_mask = BodyPartSprite((0, 0), (self.rect.width, self.rect.height))
        self.feet = BodyPartSprite((self.rect.width * 0.15, self.rect.height * 0.6), (self.rect.width * 0.7, self.rect.height * 0.8))
        self.head = BodyPartSprite((0, self.rect.height * -0.2), (self.rect.width, self.rect.height * 0.5))
        self.side_mask = BodyPartSprite((0, self.rect.height * 0.3), (self.rect.width, self.rect.height * 0.4))
        self.mask = self.body_mask  # for collision with other and projectil

    def move(self, GAME: Game, CAMERA: Camera):
        global Y
        global L
        GM = GAME.partie
        try:
            self.__getattribute__("rect")
        except:
            raise AttributeError("MOB must have a rect to move")

        _dy = int((self.inertia.y) * GAME.serialized)
        _dx = int((self.x_axis * self.speed + self.inertia.x) * GAME.serialized)
        _d = Vector2(_dx, _dy)
        self.actual_speed = _d.lenght

        _movements = [self.rect.width // 4 for i in range(int(self.actual_speed / (self.rect.width // 4)))] + [self.actual_speed % (self.rect.width // 4)]

        # generation of the mask
        _sprite = pygame.sprite.Sprite()
        _sprite.rect = GM.map.image.get_rect(topleft=(0, 0))
        _sprite.mask = GM.map.mask.copy()
        for player in GM.players:
            if not player.phatom and player.visible and player is not self:
                _sprite.mask.draw(player.mask, player.rect.topleft)

        j = 0
        for i in _movements:
            if _d.arg is not None:  # arg is none we have no movement
                __d = _d.unity * i
                __d = self.collide_reaction(__d, i, _sprite, GAME.serialized)
                self.rect.move_ip(*__d)
            else:
                __d = self.collide_reaction(Vector2(0, 0), 0, _sprite, GAME.serialized)
                self.rect.move_ip(*__d)

    def collide_reaction(self, __d: Vector2, i: int, target, serialized):
        _n = self.body_mask.collide_normal((__d + self.rect.topleft)(), target,)
        if _n.arg is not None:  # * arg is not none then we have collision
            # collision on side
            if self.side_mask.collide((__d + self.rect.topleft)(), target):
                self.grounded = False
                if _n.x > 0:
                    while self.side_mask.collide((__d + self.rect.topleft)(), target) and abs(__d.x) < i * 2:
                        __d.x += 1
                    if __d.y:
                        __d.y += 0.5 * __d.y / abs(__d.y)
                elif _n.x < 0:
                    while self.side_mask.collide((__d + self.rect.topleft)(), target) and abs(__d.x) < i * 2:
                        __d.x -= 1
                    if __d.y:
                        __d.y += 0.5 * __d.y / abs(__d.y)
            # update of the collision
            _n = self.body_mask.collide_normal((__d + self.rect.topleft)(), target)
            if _n.arg is None:
                pass
            elif self.actual_speed / serialized > self.speed * 2 and __d.lenght > 0:  # boucing effect
                _angle = 2 * _n.arg - __d.arg  # the absolute angle of our new vector
                _dangle = __d.arg - _angle  # the diff of angle between the two
                self.inertia.x = - \
                    (cos(_dangle) * __d.x + sin(_dangle) * __d.y) * \
                    self.life_multiplicator / serialized
                self.inertia.y = - \
                    (sin(_dangle) * __d.x + cos(_dangle) * __d.y) * \
                    2 * self.life_multiplicator / serialized
            # collision on feet
            elif _n.arg < -pi / 4 and _n.arg > -3 * pi / 4 and self.feet.collide((__d + self.rect.topleft)(), target):
                self.inertia.y = 0
                self.grounded = True
                # unclip
                while self.body_mask.collide((__d + self.rect.topleft)(), target) and __d.y > 0:
                    __d.y -= 1
                _test = (__d + self.rect.topleft)
                _test.y -= i  # test climbing
                if not self.body_mask.collide(_test(), target) and abs(__d.x) > 0 and self.body_mask.collide((__d + self.rect.topleft)(), target):
                    __d.y -= i
            # collision of head
            elif _n.arg > pi / 4 and _n.arg < 3 * pi / 4 and self.head.collide((__d + self.rect.topleft)(), target):
                self.grounded = False
                _NE = (__d + self.rect.topleft)
                _NE.x -= i * 1.2
                _NW = (__d + self.rect.topleft)
                _NW.x += i * 1.2
                # test displacement on right
                if not self.body_mask.collide(_NE(), target):
                    __d.x -= i * 1.2
                # test displacement on left
                elif not self.body_mask.collide(_NW(), target):
                    __d.x += i * 1.2
                else:  # no alternative then stop the jump
                    self.inertia.y = 0
                    while self.body_mask.collide((__d + self.rect.topleft)(), target) and __d.y < 0:
                        __d.y += 1
            # collision undefined
            else:
                _last_n = _n.lenght

                while self.body_mask.collide((__d + self.rect.topleft)(), target) and __d.lenght < i * 3:
                    __d += _n.unity
                    _n = self.body_mask.collide_normal((__d + self.rect.topleft)(), target)
                    if _n.lenght >= _last_n:
                        break
                    _last_n = _n.lenght
        else:  # * else no collison so no operation
            self.grounded = False
        if not self.body_mask.collide((__d + self.rect.topleft)(), target):
            return __d
        else:
            # in case the reaction fail or like with boucing
            return Vector2(0, 0)

    def handle(self, event: pygame.event.Event):
        """methode appele a chaque event"""
        match event.type:
            case tl.GRAVITY:
                if not self.grounded and self.inertia.y < self.speed * 1.5:
                    self.inertia.y += 9.81 * event.serialized * self.gravity
                if self.inertia.x != 0:
                    if abs(self.inertia.x) < self.speed / 2:
                        _d = (0 - self.inertia.x) / 2
                    else:
                        _d = -9.81 * event.serialized * self.gravity * Axis.sign(self.inertia.x) * 0.5
                    self.inertia.x += _d
            case _:
                ...

    def update(self, GAME, CAMERA):
        if not self.phatom:
            self.move(GAME, CAMERA)

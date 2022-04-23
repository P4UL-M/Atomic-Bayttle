import pygame
from .MOTHER import MOB
from src.tools.tools import animation_Manager, sprite_sheet, Keyboard, Vector2, MixeurAudio
from src.tools.constant import TEAM, EndPartie, ENDTURN, DEATH, PATH
import src.tools.constant as tl
from src.game_effect.particule import Particule, textParticle
from src.weapons.WEAPON import Sniper, Launcher, Chainsaw
from src.weapons.manager import inventory

INFO = pygame.display.Info()


class Player(MOB):

    def __init__(self, name, pos, size, team, group, id_weapon):
        """parametres :
            - pos : les position de base
            - size : la taille du sprite
            - team : la team d'image à charger
            - group : le group de sprite a ajouter le sprite
        """
        # initialisation de la classe mere permettant de faire de cette classe un sprite
        super().__init__(pos, size, group)
        self.name = name
        self.life = 1

        self.manager: animation_Manager = animation_Manager()
        self.right_direction = True

        self.jump_force = 8
        self.double_jump = 0
        self.jump_cooldown = 0
        self.cooldown_double_jump = 400

        # for action
        self.lock = False
        self.input_lock = True
        self.weapon_manager = inventory()  # mettre travail de Joseph ici

        self.load_team(team)

    @property
    def image(self) -> pygame.Surface:
        surf = self.manager.surface
        if self.right_direction:
            return surf
        else:
            # ! if too much loss of perf we will stock both
            return pygame.transform.flip(surf, True, False)

    def load_team(self, team):
        # load all annimation in annimation manager
        idle = sprite_sheet(PATH / "assets" / "perso" /
                            team / "idle.png", TEAM[team]["idle"])
        run = sprite_sheet(PATH / "assets" / "perso" /
                           team / "run.png", TEAM[team]["run"])
        jump = sprite_sheet(PATH / "assets" / "perso" /
                            team / "jump.png", TEAM[team]["jump"])
        fall = sprite_sheet(PATH / "assets" / "perso" /
                            team / "fall.png", TEAM[team]["fall"])
        ground = sprite_sheet(PATH / "assets" / "perso" /
                              team / "ground.png", TEAM[team]["ground"])
        emote = sprite_sheet(PATH / "assets" / "perso" /
                             team / "emote.png", TEAM[team]["emote"])
        self.manager.add_annimation(
            "idle", idle, 10 * TEAM[team]["speed_factor"])
        self.manager.add_annimation("run", run, 10 * TEAM[team]["speed_factor"])
        self.manager.add_annimation("jump", jump, 10)
        self.manager.add_annimation("fall", fall, 10)
        self.manager.add_annimation("ground", ground, 15)
        self.manager.add_annimation("emote", emote, 7)
        self.manager.add_link("jump", "fall")
        self.manager.add_link("ground", "idle")
        self.manager.add_link("emote", "idle")
        self.manager.load("idle")

    def respawn(self):
        self.inertia.y = 0
        self.inertia.x = 0
        self.life_multiplicator = 0
        if not self.lock:
            pygame.event.post(pygame.event.Event(ENDTURN))

    def handle(self, event: pygame.event.Event, GAME, CAMERA):
        """methode appele a chaque event"""
        match event.type:
            case pygame.KEYUP if event.key == Keyboard.end_turn.key and not self.lock:
                pygame.event.post(pygame.event.Event(ENDTURN))
            case tl.IMPACT:
                _dist = Vector2(self.rect.centerx - event.x, self.rect.centery - event.y)
                if _dist.lenght < event.radius + self.rect.width:
                    if not event.friendly_fire and not self.lock:
                        return
                    self.inertia += _dist * self.life_multiplicator * event.multiplicator_repulsion
                    self.life_multiplicator += event.damage / 100
                    x = self.rect.centerx
                    y = self.rect.centery
                    size = 7 + event.damage**1.15 / 6
                    GAME.partie.group_particle.add(textParticle(30, (x, y), Vector2(0, -1), 1, int(str(event.damage)[0]), (size, size)))
                    if len(str(event.damage)) > 1:
                        GAME.partie.group_particle.add(textParticle(30, (x + size + 1, y), Vector2(0, -1), 1, int(str(event.damage)[1]), (size, size)))
                    MixeurAudio.play_effect(PATH / "assets" / "sound" / "voice_hit.wav", 0.20)
            case pygame.KEYDOWN:
                if not self.lock and self.input_lock:
                    self.input_lock = False
        super().handle(event)
        self.weapon_manager.handle(event, self, GAME, CAMERA)

    def update(self, GAME, CAMERA):
        GM = GAME.partie
        if not self.lock:
            self.x_axis.update(Keyboard.right.is_pressed,
                               Keyboard.left.is_pressed)
            self.y_axis.update(Keyboard.up.is_pressed,
                               Keyboard.down.is_pressed)
            if Keyboard.jump.is_pressed:
                if self.jump_cooldown < pygame.time.get_ticks() and (self.grounded or self.double_jump):
                    self.double_jump = self.grounded
                    self.inertia.y = -self.jump_force
                    self.grounded = False
                    self.jump_cooldown = pygame.time.get_ticks() + self.cooldown_double_jump
                    self.manager.load("jump")
                    for i in range(5):
                        GM.group_particle.add(Particule(10, Vector2(self.rect.left + self.image.get_width(
                        ) // 2, self.rect.bottom), self.image.get_width() // 2, Vector2(1, -2), 2, pygame.Color(20, 20, 0)))
            if Keyboard.interact.is_pressed:
                ...
            if Keyboard.inventory.is_pressed:
                ...

            if self.x_axis.value > 0:  # tempo variable so keep in cache until real changement of direction
                self.right_direction = True
            elif self.x_axis.value < 0:
                self.right_direction = False

            # * walking particle here
            if self.grounded:
                self.double_jump = True
                if self.actual_speed > 1 and pygame.time.get_ticks() % 7 == 0:
                    GM.group_particle.add(Particule(10, Vector2(self.rect.left + self.image.get_width() // 2, self.rect.bottom),
                                          self.image.get_width() // 2, Vector2(-self.x_axis.value * 2, 0), 0.25 * self.actual_speed, pygame.Color(20, 20, 0)))

            # * CAMERA Update of the player
            x, y = CAMERA.to_virtual(INFO.current_w / 2, INFO.current_h / 2)
            _x, _y = (self.rect.left, self.rect.top)
            CAMERA.x += (_x - x) * 0.0001
            CAMERA.y += (_y - y) * 0.0001
            # * Effect of dezoom relatif to speed
            zoom_target = 2.5 * (1 / (self.actual_speed * 0.1 + 1)
                                 ) * self.weapon_manager.zoom_factor
            CAMERA.zoom += (zoom_target - CAMERA.zoom) * 0.01
        elif not self.phatom:
            self.x_axis.update()
            self.y_axis.update()

        # * annimation
        if self.manager._loaded_name not in ["jump", "ground", "emote"]:
            if self.actual_speed > 1:
                if not self.grounded:
                    self.manager.load("fall")
                elif self.manager._loaded_name == "fall":
                    self.manager.load("ground")
                else:
                    self.manager.load("run")
                    self.manager.annim_speed_factor = 1 + self.actual_speed * 0.05
            elif self.grounded:
                if self.manager._loaded_name == "fall":
                    self.manager.load("ground")
                else:
                    self.manager.load("idle")
                    self.manager.annim_speed_factor = 1
        # * death
        if self.visible:
            if self.rect.bottom > GM.map.water_level:
                MixeurAudio.play_effect(tl.PATH / "assets" / "sound" / "fall_in_water.wav", 0.5)
                ev = pygame.event.Event(DEATH, {"player": self})
                pygame.event.post(ev)
                self.visible = False
            elif (Vector2(*self.rect.topleft) - Vector2(*GM.map.rect.center)).lenght > 2500 or self.rect.topleft[0] < GM.map.rect.left or self.rect.topleft[0] > GM.map.rect.right:
                ev = pygame.event.Event(DEATH, {"player": self})
                pygame.event.post(ev)
                self.visible = False
        # * inertia and still update if inactive
        if self.visible:
            super().update(GAME, CAMERA)
        # after move so in final
        self.weapon_manager.update(self, GAME, CAMERA)

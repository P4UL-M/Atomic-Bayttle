import pygame
from pygame.locals import *
from pygame_easy_menu import *
from pygame_easy_menu.tools import *
from src.tools.tools import *
from src.tools.constant import PATH
from src.menu_main import animated_sprite

GAME=None
CAMERA=None
game=None

def end_screen(winner, loser):
    """Corresponding to the screen once the game is finished"""
    CAMERA._off_screen = pygame.Surface((1920, 1080), flags=HWSURFACE + HWACCEL)
    CAMERA.HUD = False
    CAMERA.zoom = 1
    CAMERA.maximise = False
    pygame.mouse.set_visible(True)

    game=Menu_Manager(name="end_screen", window=CAMERA._off_screen, background=PATH / "assets" / "menu" / "background_sheet.png")
    game.running=True

    principal=Menu("Principal")


    @principal.add_sprite
    def name():
        _sprite=sprite(
            name="name",
            path=PATH / "assets" / "menu" / "end" / "{}.png".format(winner),
            manager=game
        )

        _sprite.set_position(Vector2(0.5,0.6))
        _sprite.set_scale(Vector2(5.1,5.1))

        return _sprite

    @principal.add_sprite
    def wins():
        _sprite=sprite(
            name="wins",
            path=PATH / "assets" / "menu" / "end" / "wins.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.5,0.75))
        _sprite.set_scale(Vector2(5.1,5.1))

        return _sprite

    @principal.add_sprite
    def winner_sprite():
        manager=animation_Manager()
        if winner=="perso_2":
            spritesheet=sprite_sheet(PATH / "assets" / "perso" / "perso_2" / "idle.png", (42,29))
            spritesheet.config((420,290))
        elif winner=="perso_4":
            spritesheet=sprite_sheet(PATH / "assets" / "perso" / "perso_4" / "idle.png", (31,28))
            spritesheet.config((310,280))
        else:
            spritesheet=sprite_sheet(PATH / "assets" / "perso" / winner / "idle.png", (24,28))
            spritesheet.config((240,280))

        if winner!="perso_1":
            manager.add_annimation("winner", spritesheet, 7)
        else:
            manager.add_annimation("winner", spritesheet, 10)

        _sprite=animated_sprite(
            name="winner",
            manager=game,
            animation_manager=manager
        )

        _sprite.set_position(Vector2(0.4,0.25))

        return _sprite

    @principal.add_sprite
    def loser_sprite():
        manager=animation_Manager()
        if loser=="perso_1":
            spritesheet=sprite_sheet(PATH / "assets" / "perso" / "perso_1" / "idle.png", (64,40))
            spritesheet.config((512,320))
        elif loser=="perso_2":
            spritesheet=sprite_sheet(PATH / "assets" / "perso" / "perso_2" / "idle.png", (72,32))
            spritesheet.config((576,256))
        else:
            spritesheet=sprite_sheet(PATH / "assets" / "perso" / loser / "idle.png", (34,30))
            spritesheet.config((272,240))

        manager.add_annimation("loser", spritesheet, 7)

        _sprite=animated_sprite(
            name="loser",
            manager=game,
            animation_manager=manager
        )

        _sprite.set_position(Vector2(0.4,0.75))

        return _sprite

    @principal.add_sprite
    def exit():
        _button=Button(
            name="exit",
            path=PATH / "assets" / "menu" / "end" / "exit.png",
            manager=game
        )

        _button.set_position(Vector2(0.8,0.85))
        _button.set_scale(Vector2(4.0,4.0))

        return _button

    @principal.add_sprite
    def menu():
        _button=Button(
            name="menu",
            path=PATH / "assets" / "menu" / "end" / "menu.png",
            manager=game
        )

        _button.set_position(Vector2(0.2,0.85))
        _button.set_scale(Vector2(4.0,4.0))

        return _button

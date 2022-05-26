import pygame
from pygame.locals import *
from pygame_easy_menu import *
from pygame_easy_menu.tools import *
from src.tools.tools import *
from src.tools.constant import PATH, TEAM
from src.menu_main import animated_sprite

"""
The functionnement of this menu is the same as the menu_main.py
"""

GAME = None
CAMERA = None
game = None


def setup_manager(winner, loser):
    """Corresponding to the screen once the game is finished"""
    global game
    CAMERA._off_screen = pygame.Surface((1920, 1080), flags=HWSURFACE + HWACCEL)
    CAMERA.HUD = False
    CAMERA.zoom = 1
    CAMERA.maximise = False
    pygame.mouse.set_visible(True)

    game = Menu_Manager(name="end_screen", window=CAMERA._off_screen, background=PATH / "assets" / "menu" / "background_sheet.png")
    game.play_effect = MixeurAudio.play_effect
    game.running = True

    principal = Menu("Principal", game)

    @principal.set_setup
    def setup():
        MixeurAudio.stop("all")
        MixeurAudio.set_musique(PATH / "assets" / "music" / f"theme_{winner}.mp3", False)
        MixeurAudio.set_musique(PATH / "assets" / "music" / "main-loop.wav", True, True)

    @principal.add_sprite
    def plateform():
        _sprite = sprite(
            name="plateform",
            path=PATH / "assets" / "menu" / "end" / "plateform.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.5, 0.87))
        _sprite.set_scale(Vector2(2.9, 2.9))

        return _sprite

    @principal.add_sprite
    def button_background():
        _sprite = sprite(
            name="button_background",
            path=PATH / "assets" / "menu" / "end" / "panel.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.5, 0.2))
        _sprite.set_scale(Vector2(5.0, 5.0))

        return _sprite

    @principal.add_sprite
    def name():
        _sprite = sprite(
            name="name",
            path=PATH / "assets" / "menu" / "end" / "{}.png".format(winner),
            manager=game
        )

        _sprite.set_position(Vector2(0.5, 0.15))
        _sprite.set_scale(Vector2(7.0, 7.0))

        return _sprite

    @principal.add_sprite
    def wins():
        _sprite = sprite(
            name="wins",
            path=PATH / "assets" / "menu" / "end" / "wins.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.5, 0.25))
        _sprite.set_scale(Vector2(7.0, 7.0))

        return _sprite

    @principal.add_sprite
    def totem1():
        _sprite = sprite(
            name="totem1",
            path=PATH / "assets" / "menu" / "end" / "totem1.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.1, 0.45))
        _sprite.set_scale(Vector2(5.0, 5.0))

        return _sprite

    @principal.add_sprite
    def totem2():
        _sprite = sprite(
            name="totem2",
            path=PATH / "assets" / "menu" / "end" / "totem2.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.9, 0.45))
        _sprite.set_scale(Vector2(5.0, 5.0))

        return _sprite

    @principal.add_sprite
    def chest():
        _sprite = sprite(
            name="chest",
            path=PATH / "assets" / "menu" / "end" / "chest.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.5, 0.652))
        _sprite.set_scale(Vector2(6.0, 6.0))

        return _sprite

    @principal.add_sprite
    def winner_sprite():
        manager = animation_Manager()
        spritesheet = sprite_sheet(PATH / "assets" / "perso" / winner / "emote.png", TEAM[winner]["emote"])
        spritesheet.config(tuple(i * 10 for i in TEAM[winner]["emote"]))

        manager.add_annimation("winner", spritesheet, 7)
        manager.load("winner")

        _sprite = animated_sprite(
            name="winner",
            manager=game,
            animation_manager=manager
        )

        _sprite.set_position(Vector2(0.32, 0.612))
        _sprite.rect.y = principal.get_sprite("plateform").rect.top - _sprite.manager.actual_surface.get_height()

        return _sprite

    @principal.add_sprite
    def loser_sprite():
        manager = animation_Manager()
        spritesheet = sprite_sheet(PATH / "assets" / "perso" / loser / "losed.png", TEAM[loser]["losed"][:2])
        spritesheet.config(tuple(i * 8 for i in TEAM[loser]["losed"][:2]))

        manager.add_annimation("loser", spritesheet, 12)
        manager.load("loser")

        _sprite = animated_sprite(
            name="loser",
            manager=game,
            animation_manager=manager
        )

        _sprite.set_position(Vector2(0.75, 0.66))
        _sprite.rect.y = principal.get_sprite("plateform").rect.top - _sprite.manager.actual_surface.get_height() + 8 * TEAM[loser]["losed"][2]

        return _sprite

    @principal.add_sprite
    def exit():
        _button = Button(
            name="exit",
            path=PATH / "assets" / "menu" / "end" / "exit.png",
            manager=game
        )

        _button.set_position(Vector2(0.8, 0.87))
        _button.set_scale(Vector2(5.1, 5.1))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def exit():
            game.destroy()

        return _button

    @principal.add_sprite
    def menu():
        _button = Button(
            name="menu",
            path=PATH / "assets" / "menu" / "end" / "menu.png",
            manager=game
        )

        _button.set_position(Vector2(0.2, 0.87))
        _button.set_scale(Vector2(5.1, 5.1))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def start_menu():
            GAME.start_menu()

        return _button

    @principal.add_sprite
    def palmer1():
        _sprite = sprite(
            name="palmer1",
            path=PATH / "assets" / "menu" / "end" / "palmer1.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.05, 0.85))
        _sprite.set_scale(Vector2(4.0, 4.0))

        return _sprite

    @principal.add_sprite
    def palmer2():
        _sprite = sprite(
            name="palmer2",
            path=PATH / "assets" / "menu" / "end" / "palmer2.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.96, 0.85))
        _sprite.set_scale(Vector2(4.0, 4.0))

        return _sprite

    game.actual_menu = principal

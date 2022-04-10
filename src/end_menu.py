import pygame
from pygame.locals import *
from pygame_easy_menu import *
from pygame_easy_menu.tools import *
from src.tools.tools import *
from src.tools.constant import PATH, TEAM
from src.menu_main import animated_sprite

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
    game.running = True

    principal = Menu("Principal", game)

    @principal.add_sprite
    def name():
        _sprite = sprite(
            name="name",
            path=PATH / "assets" / "menu" / "end" / "{}.png".format(winner),
            manager=game
        )

        _sprite.set_position(Vector2(0.5, 0.6))
        _sprite.set_scale(Vector2(7.0, 7.0))

        return _sprite

    @principal.add_sprite
    def wins():
        _sprite = sprite(
            name="wins",
            path=PATH / "assets" / "menu" / "end" / "wins.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.5, 0.75))
        _sprite.set_scale(Vector2(7.0, 7.0))

        return _sprite

    @principal.add_sprite
    def winner_sprite():
        manager = animation_Manager()
        spritesheet = sprite_sheet(PATH / "assets" / "perso" / winner / "emote.png", TEAM[winner]["emote"])
        spritesheet.config(tuple(i * 10 for i in TEAM[winner]["emote"]))

        if winner != "perso_1":
            manager.add_annimation("winner", spritesheet, 7)
        else:
            manager.add_annimation("winner", spritesheet, 10)
        manager.load("winner")

        _sprite = animated_sprite(
            name="winner",
            manager=game,
            animation_manager=manager
        )

        _sprite.set_position(Vector2(0.4, 0.25))

        return _sprite

    @principal.add_sprite
    def loser_sprite():
        manager = animation_Manager()
        spritesheet = sprite_sheet(PATH / "assets" / "perso" / loser / "losed.png", TEAM[loser]["losed"])
        spritesheet.config(tuple(i * 8 for i in TEAM[loser]["losed"]))

        manager.add_annimation("loser", spritesheet, 5)
        manager.load("loser")

        _sprite = animated_sprite(
            name="loser",
            manager=game,
            animation_manager=manager
        )

        _sprite.set_position(Vector2(0.6, 0.25))

        return _sprite

    @principal.add_sprite
    def exit():
        _button = Button(
            name="exit",
            path=PATH / "assets" / "menu" / "end" / "exit.png",
            manager=game
        )

        _button.set_position(Vector2(0.8, 0.85))
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

        _button.set_position(Vector2(0.2, 0.85))
        _button.set_scale(Vector2(5.1, 5.1))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def start_menu():
            GAME.start_menu()

        return _button

    game.actual_menu = principal

import pygame
from pygame.locals import *
from pygame_easy_menu import *
from pygame_easy_menu.tools import *
from src.tools.tools import *
from src.tools.constant import PATH
from math import sin

GAME = None
CAMERA = None

game = None


class CursorButton(Button, sprite):
    def __init__(self, name, path, manager, isactive=True, layer=0, pos: Vector2 = Vector2(0, 0)):
        super().__init__(name, path, manager, isactive, layer)
        self.cursor_position = pos


class animated_sprite(sprite):  # class without surface set and annimated
    def __init__(self, name, manager, animation_manager, isactive=True, layer=0, pos: Vector2 = Vector2(0, 0)):
        super(sprite, self).__init__()
        self.name = name
        self.layer = layer
        self.isactive = isactive
        self._manager = manager
        self.manager = animation_manager

        self.handles = []

        self.rect = self.image.get_rect(topleft=(0, 0))
        self.initial_size = Vector2(
            self.image.get_width(), self.image.get_height())

    @property
    def image(self):
        return self.manager.surface

    def set_scale(self, sca: Vector2, center=True): ...


sprite_sheet.dico = {pygame.K_a: 0, pygame.K_b: 1, pygame.K_c: 2, pygame.K_d: 3, pygame.K_e: 4, pygame.K_f: 5, pygame.K_g: 6, pygame.K_h: 7, pygame.K_i: 8, pygame.K_j: 9,
                     pygame.K_k: 10, pygame.K_l: 11, pygame.K_m: 12, pygame.K_n: 13, pygame.K_o: 14, pygame.K_p: 15, pygame.K_q: 16, pygame.K_r: 17, pygame.K_s: 18, pygame.K_t: 19, pygame.K_u: 20,
                     pygame.K_v: 21, pygame.K_w: 22, pygame.K_x: 23, pygame.K_y: 24, pygame.K_z: 25, pygame.K_0: 26, pygame.K_1: 27, pygame.K_2: 28, pygame.K_3: 29, pygame.K_4: 30, pygame.K_5: 31,
                     pygame.K_6: 32, pygame.K_7: 33, pygame.K_8: 34, pygame.K_9: 35, pygame.K_EXCLAIM: 36, pygame.K_COMMA: 37, pygame.K_SEMICOLON: 38, pygame.K_LALT: 39, pygame.K_BACKSPACE: 40,
                     pygame.K_LCTRL: 41, pygame.K_COLON: 42, pygame.K_RETURN: 43, pygame.K_ESCAPE: 44, pygame.K_LSHIFT: 45, pygame.K_SPACE: 46, pygame.K_TAB: 47, pygame.K_DOWN: 48, pygame.K_LEFT: 49,
                     pygame.K_RIGHT: 50, pygame.K_UP: 51}


def setup_manager():
    global game
    CAMERA._off_screen = pygame.Surface(
        (1920, 1080), flags=HWSURFACE + HWACCEL)
    CAMERA.HUD = False
    CAMERA.zoom = 1
    CAMERA.maximise = False
    MixeurAudio.set_musique(path=PATH / "assets" / "music" / "main-loop.wav")
    pygame.mouse.set_visible(True)

    game = Menu_Manager(name="Atomic Bay'ttle", window=CAMERA._off_screen,
                        background=PATH / "assets" / "menu" / "background_sheet.png")
    game.play_effect = MixeurAudio.play_effect
    game.running = True
    game.set_font(PATH / "assets" / "menu" / "rules" / "font.ttf")

    principal = Menu("Principal", game, childs=["Settings", "Play", "Rules"])
    settings_menu = Menu(
        "Settings", game, parent="Principal", childs="Keybinds")
    keybind_menu = Menu("Keybinds", game, parent="Settings")
    play_menu = Menu("Play", game, parent="Principal")
    rules_menu = Menu("Rules", game, parent="Principal")

    # region Principal menu

    @principal.set_setup
    def princ_setup():
        MixeurAudio.load(PATH)
        Keyboard.load(PATH)

    @principal.add_sprite
    def exit_button():
        _button = Button(
            name='exit',
            path=PATH / "assets" / "menu" / "principal" / "exitbutton.png",
            manager=game
        )

        _button.set_position(Vector2(0.5, 0.83))
        _button.set_scale(Vector2(0.56, 0.56))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def stop():
            game.destroy()

        return _button

    @principal.add_sprite
    def rules_button():
        _button = Button(
            name='rules',
            path=PATH / "assets" / "menu" / "principal" / "rulesbutton.png",
            manager=game
        )

        _button.set_position(Vector2(0.5, 0.55))
        _button.set_scale(Vector2(0.56, 0.56))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def rules():
            game.actual_menu = principal.get_child("Rules")

        return _button

    @principal.add_sprite
    def settings_button():
        _button = Button(
            name="settings",
            path=PATH / "assets" / "menu" / "principal" / "settingsbutton.png",
            manager=game
        )

        _button.set_position(Vector2(0.5, 0.69))
        _button.set_scale(Vector2(0.56, 0.56))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def settings():
            game.actual_menu = principal.get_child("Settings")

        return _button

    @principal.add_sprite
    def play_button():
        _button = Button(
            name="play",
            path=PATH / "assets" / "menu" / "principal" / "playbutton.png",
            manager=game
        )

        _button.set_position(Vector2(0.5, 0.4))
        _button.set_scale(Vector2(0.56, 0.56))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def play():
            game.actual_menu = principal.get_child("Play")

        @_button.Event(pygame.KEYDOWN)
        def start(event):
            if event.key == Keyboard.interact.key:
                game.actual_menu = principal.get_child("Play")

        return _button

    @principal.add_sprite
    def title_sprite():
        _button = sprite(
            name="title",
            path=PATH / "assets" / "menu" / "principal" / "atomic_bay'ttle.png",
            manager=game
        )

        _button.set_position(Vector2(0.5, 0.17))
        _button.set_scale(Vector2(10.0, 9.0))

        return _button

    game.actual_menu = principal

    # endregion

    # region Settings menu

    @settings_menu.set_setup
    def setup():
        cursor_effects = settings_menu.get_sprite("effects_cursor")
        effects_sprite = settings_menu.get_sprite(
            f"effects_volume{int(MixeurAudio.volume_effect*10)}")
        _pos = Vector2(*effects_sprite.rect.center)
        _offset = effects_sprite.cursor_position
        cursor_effects.set_position(_pos + _offset)

        cursor_music = settings_menu.get_sprite("music_cursor")
        music_sprite = settings_menu.get_sprite(
            f"music_volume{int(MixeurAudio.volume_musique*10)}")
        _pos = Vector2(*music_sprite.rect.center)
        _offset = music_sprite.cursor_position
        cursor_music.set_position(_pos + _offset)

    @settings_menu.add_sprite
    def settings_bg():
        _button = Button(
            name='settings_bg',
            path=PATH / "assets" / "menu" / "settings" / "green_board.png",
            manager=game
        )

        _button.set_position(Vector2(0.5, 0.5))
        _button.set_scale(Vector2(7.5, 7.5))

        return _button

    @settings_menu.add_sprite
    def goback_button():
        _button = Button(
            name='go back',
            path=PATH / "assets" / "menu" / "settings" / "gobackbutton.png",
            manager=game
        )

        _button.set_position(Vector2(0.18, 0.85))
        _button.set_scale(Vector2(2.0, 2.0))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def goback():
            game.actual_menu = settings_menu.get_parent()

        return _button

    # region volume_button
    @settings_menu.add_sprite
    def effects_volume0():
        _button = CursorButton(
            name="effects_volume0",
            path=PATH / "assets" / "menu" / "settings" / "leftslide0.png",
            manager=game,
            pos=Vector2(3, 0)
        )

        _button.set_scale(Vector2(4.58, 4.58))
        _button.set_position(Vector2(0.2464, 0.575))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects0():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume1():
        _button = CursorButton(
            name="effects_volume1",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.2687, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects1():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.1
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume2():
        _button = CursorButton(
            name="effects_volume2",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.2895, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects2():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.2
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume3():
        _button = CursorButton(
            name="effects_volume3",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.3104, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects3():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.3
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume4():
        _button = CursorButton(
            name="effects_volume4",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.3312, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects4():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.4
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume5():
        _button = CursorButton(
            name="effects_volume5",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.3520, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects5():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.5
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume6():
        _button = CursorButton(
            name="effects_volume6",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.3729, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects6():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.6
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume7():
        _button = CursorButton(
            name="effects_volume7",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.3937, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects7():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.7
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume8():
        _button = CursorButton(
            name="effects_volume8",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.4145, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects8():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.8
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume9():
        _button = CursorButton(
            name="effects_volume9",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.4353, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects9():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.9
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume10():
        _button = CursorButton(
            name="effects_volume10",
            path=PATH / "assets" / "menu" / "settings" / "rightslide0.png",
            manager=game,
            pos=Vector2(-3, 0)
        )

        _button.set_position(Vector2(0.457, 0.575))
        _button.set_scale(Vector2(4.58, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects10():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 1.0
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume0():
        _button = CursorButton(
            name="music_volume0",
            path=PATH / "assets" / "menu" / "settings" / "leftslide0.png",
            manager=game,
            pos=Vector2(3, 0)
        )

        _button.set_scale(Vector2(4.58, 4.58))
        _button.set_position(Vector2(0.540, 0.575))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music0():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume1():
        _button = CursorButton(
            name="music_volume1",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.5624, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music1():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.1
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume2():
        _button = CursorButton(
            name="music_volume2",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.5833, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music2():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.2
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume3():
        _button = CursorButton(
            name="music_volume3",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.6041, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music3():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.3
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume4():
        _button = CursorButton(
            name="music_volume4",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.6249, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music4():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.4
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume5():
        _button = CursorButton(
            name="music_volume5",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.6458, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music5():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.5
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume6():
        _button = CursorButton(
            name="music_volume6",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.6666, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music6():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.6
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume7():
        _button = CursorButton(
            name="music_volume7",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.6874, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music7():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.7
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume8():
        _button = CursorButton(
            name="music_volume8",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.7083, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music8():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.8
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume9():
        _button = CursorButton(
            name="music_volume9",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
        )

        _button.set_position(Vector2(0.7291, 0.575))
        _button.set_scale(Vector2(4.07, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music9():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.9
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume10():
        _button = CursorButton(
            name="music_volume10",
            path=PATH / "assets" / "menu" / "settings" / "rightslide0.png",
            manager=game,
            pos=Vector2(-3, 0)
        )

        _button.set_position(Vector2(0.751, 0.575))
        _button.set_scale(Vector2(4.58, 4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music10():
            _pos = Vector2(*_button.rect.center) + _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 1
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    # endregion

    @settings_menu.add_sprite
    def effects_cursor():
        _button = Button(
            name="effects_cursor",
            path=PATH / "assets" / "menu" / "settings" / "cursor.png",
            manager=game
        )

        _button.set_scale(Vector2(4.58, 4.58))

        return _button

    @settings_menu.add_sprite
    def music_cursor():
        _button = Button(
            name="music_cursor",
            path=PATH / "assets" / "menu" / "settings" / "cursor.png",
            manager=game
        )

        _button.set_scale(Vector2(4.58, 4.58))

        return _button

    @settings_menu.add_sprite
    def effects_button():
        _button = sprite(
            name="effects",
            path=PATH / "assets" / "menu" / "settings" / "effectsbutton.png",
            manager=game
        )

        _button.set_position(Vector2(0.353, 0.50))
        _button.set_scale(Vector2(2.6, 2.6))

        return _button

    @settings_menu.add_sprite
    def music_button():
        _button = sprite(
            name="effects",
            path=PATH / "assets" / "menu" / "settings" / "musicbutton.png",
            manager=game
        )

        _button.set_position(Vector2(0.647, 0.50))
        _button.set_scale(Vector2(2.6, 2.6))

        return _button

    @settings_menu.add_sprite
    def chain8():
        _button = sprite(
            name="chain8",
            path=PATH / "assets" / "menu" / "settings" / "chain.png",
            manager=game
        )

        _button.set_position(Vector2(0.75, 0.42))
        _button.set_scale(Vector2(2.0, 2.0))

        return _button

    @settings_menu.add_sprite
    def chain7():
        _button = sprite(
            name="chain6",
            path=PATH / "assets" / "menu" / "settings" / "chain.png",
            manager=game
        )

        _button.set_position(Vector2(0.544, 0.42))
        _button.set_scale(Vector2(2.0, 2.0))

        return _button

    @settings_menu.add_sprite
    def chain6():
        _button = sprite(
            name="chain6",
            path=PATH / "assets" / "menu" / "settings" / "chain.png",
            manager=game
        )

        _button.set_position(Vector2(0.25, 0.42))
        _button.set_scale(Vector2(2.0, 2.0))

        return _button

    @settings_menu.add_sprite
    def chain5():
        _button = sprite(
            name="chain5",
            path=PATH / "assets" / "menu" / "settings" / "chain.png",
            manager=game
        )

        _button.set_position(Vector2(0.456, 0.42))
        _button.set_scale(Vector2(2.0, 2.0))

        return _button

    @settings_menu.add_sprite
    def volume_button():
        _button = sprite(
            name="volume",
            path=PATH / "assets" / "menu" / "settings" / "volumebutton.png",
            manager=game
        )

        _button.set_position(Vector2(0.5, 0.36))
        _button.set_scale(Vector2(4.0, 4.0))

        return _button

    @settings_menu.add_sprite
    def chain3():
        _button = sprite(
            name="chain3",
            path=PATH / "assets" / "menu" / "settings" / "chain.png",
            manager=game
        )

        _button.set_position(Vector2(0.26, 0.27))
        _button.set_scale(Vector2(2.0, 2.0))

        return _button

    @settings_menu.add_sprite
    def chain4():
        _button = sprite(
            name="chain4",
            path=PATH / "assets" / "menu" / "settings" / "chain.png",
            manager=game
        )

        _button.set_position(Vector2(0.74, 0.27))
        _button.set_scale(Vector2(2.0, 2.0))

        return _button

    @settings_menu.add_sprite
    def settings_title():
        _button = sprite(
            name="title",
            path=PATH / "assets" / "menu" / "settings" / "settingsbutton2.png",
            manager=game
        )

        _button.set_position(Vector2(0.5, 0.18))
        _button.set_scale(Vector2(4.0, 4.0))

        return _button

    @settings_menu.add_sprite
    def chain1():
        _button = sprite(
            name="chain1",
            path=PATH / "assets" / "menu" / "settings" / "smallchain.png",
            manager=game
        )

        _button.set_position(Vector2(0.26, 0.085))
        _button.set_scale(Vector2(2.0, 2.0))

        return _button

    @settings_menu.add_sprite
    def chain2():
        _button = sprite(
            name="chain2",
            path=PATH / "assets" / "menu" / "settings" / "smallchain.png",
            manager=game
        )

        _button.set_position(Vector2(0.74, 0.085))
        _button.set_scale(Vector2(2.0, 2.0))

        return _button

    @settings_menu.add_sprite
    def keybinds_button():
        _button = Button(
            name="keybinds_button",
            path=PATH / "assets" / "menu" / "settings" / "keybindsbutton.png",
            manager=game
        )

        _button.set_position(Vector2(0.5, 0.7))
        _button.set_scale(Vector2(4.0, 3.0))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def keybinds_change():
            game.actual_menu = settings_menu.get_child("Keybinds")

        return _button

    # endregion

    # region Keybinds_menu

    @keybind_menu.add_sprite
    def keybind_bg():
        _button = sprite(
            name="keybind_bg",
            path=PATH / "assets" / "menu" / "keybinds" / "yellow_board.png",
            manager=game
        )

        _button.set_position(Vector2(0.5, 0.5))
        _button.set_scale(Vector2(7.0, 7.0))

        return _button

    @keybind_menu.add_sprite
    def goback():
        _button = Button(
            name='go_back2',
            path=PATH / "assets" / "menu" / "keybinds" / "gobackbutton2.png",
            manager=game
        )

        _button.set_position(Vector2(0.18, 0.85))
        _button.set_scale(Vector2(2.0, 2.0))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def goback():
            game.actual_menu = keybind_menu.get_parent()

        return _button

    @keybind_menu.add_sprite
    def scrollzone():
        _panel = ScrollableBox(
            name="panel",
            size=(int(keybind_menu._manager.screen.get_width() * 0.8),
                  int(keybind_menu._manager.screen.get_height() * 0.68)),
            manager=game,
            path=PATH / "assets" / "menu" / "keybinds" / "cursor.png"
        )

        _panel.set_position(Vector2(0.5, 0.45))

        return _panel

    @keybind_menu.get_sprite("panel").add_sprite
    def movebutton():
        _sprite = sprite(
            name="movebutton",
            path=PATH / "assets" / "menu" / "keybinds" / "move.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.28, 0.1),
                             parent=keybind_menu.get_sprite("panel"))
        _sprite.set_scale(Vector2(4.0, 4.0))

        return _sprite

    @keybind_menu.get_sprite("panel").add_sprite
    def movekeyleft():
        _button = Button(
            name="movekeyleft",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(Vector2(0.54, 0.1),
                             parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.left.key]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def keyleft():
            if not _button.active:
                Keyboard.left.key = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changeleft(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.left.key = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.left.key].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def movealiasleft():
        _button = Button(
            name="movekeyleft",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(Vector2(0.62, 0.1),
                             parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.left.alias]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def aliasleft():
            if not _button.active:
                Keyboard.left.alias = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changeleft(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.left.alias = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.left.alias].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def movealiasright():
        _button = Button(
            name="movealiasright",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(Vector2(0.82, 0.1),
                             parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.right.alias]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def aliasright():
            if not _button.active:
                Keyboard.right.alias = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changeright(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.right.alias = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.right.alias].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)
        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def movekeyright():
        _button = Button(
            name="movekeyright",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(Vector2(0.74, 0.1),
                             parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.right.key]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def keyright():
            if not _button.active:
                Keyboard.right.key = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changeright(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.right.key = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.right.key].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def angle():
        _sprite = sprite(
            name="anglesprite",
            path=PATH / "assets" / "menu" / "keybinds" / "angle.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.28, 0.28),
                             parent=keybind_menu.get_sprite("panel"))
        _sprite.set_scale(Vector2(4.0, 4.0))

        return _sprite

    @keybind_menu.get_sprite("panel").add_sprite
    def angleupkey():
        _button = Button(
            name="angleupkey",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(Vector2(0.54, 0.28),
                             parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.up.key]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def keyup():
            if not _button.active:
                Keyboard.up.key = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changeup(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.up.key = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.up.key].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def angleupalias():
        _button = Button(
            name="angleupalias",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(Vector2(0.62, 0.28),
                             parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.up.alias]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def aliasup():
            if not _button.active:
                Keyboard.up.alias = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changeup(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.up.alias = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.up.alias].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def angledownkey():
        _button = Button(
            name="angledownkey",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(Vector2(0.74, 0.28),
                             parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.down.key]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def keydown():
            if not _button.active:
                Keyboard.down.key = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changedown(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.down.key = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.down.key].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def angledownalias():
        _button = Button(
            name="angledownalias",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(Vector2(0.82, 0.28),
                             parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.down.alias]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def keydown():
            if not _button.active:
                Keyboard.down.alias = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changedown(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.down.alias = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.down.alias].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def jump():
        _sprite = sprite(
            name="jumpsprite",
            path=PATH / "assets" / "menu" / "keybinds" / "jump.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.28, 0.46),
                             parent=keybind_menu.get_sprite("panel"))
        _sprite.set_scale(Vector2(4.0, 4.0))

        return _sprite

    @keybind_menu.get_sprite("panel").add_sprite
    def jumpkey():
        _button = Button(
            name="jumpkey",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(Vector2(0.54, 0.46),
                             parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.jump.key]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def keyjump():
            if not _button.active:
                Keyboard.jump.key = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changejump(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.jump.key = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.jump.key].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def jumpalias():
        _button = Button(
            name="jumpalias",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(Vector2(0.62, 0.46),
                             parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.jump.alias]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def keyjump():
            if not _button.active:
                Keyboard.jump.alias = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changejump(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.jump.alias = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.jump.alias].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def inventory():
        _sprite = sprite(
            name="inventorysprite",
            path=PATH / "assets" / "menu" / "keybinds" / "inventory.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.28, 0.64),
                             parent=keybind_menu.get_sprite("panel"))
        _sprite.set_scale(Vector2(4.0, 4.0))

        return _sprite

    @keybind_menu.get_sprite("panel").add_sprite
    def inventorykey():
        _button = Button(
            name="inventorykey",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(Vector2(0.54, 0.64),
                             parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.inventory.key]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def keyinventory():
            if not _button.active:
                Keyboard.inventory.key = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                Keyboard.save(PATH)
                _button.active = False

        @_button.Event(pygame.KEYDOWN)
        def changeinventory(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.inventory.key = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.inventory.key].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def inventoryalias():
        _button = Button(
            name="inventoryalias",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(Vector2(0.62, 0.64),
                             parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.inventory.alias]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def aliasinventory():
            if not _button.active:
                Keyboard.inventory.alias = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changeinventory(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.inventory.alias = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.inventory.alias].copy(
            )
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def shoot():
        _sprite = sprite(
            name="shootsprite",
            path=PATH / "assets" / "menu" / "keybinds" / "shoot.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.28, 0.82),
                             parent=keybind_menu.get_sprite("panel"))
        _sprite.set_scale(Vector2(4.0, 4.0))

        return _sprite

    @keybind_menu.get_sprite("panel").add_sprite
    def shootkey():
        _button = Button(
            name="shootkey",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(Vector2(0.54, 0.82),
                             parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.interact.key]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def keyshoot():
            if not _button.active:
                Keyboard.interact.key = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changeshoot(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.interact.key = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.interact.key].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def shootalias():
        _button = Button(
            name="shootalias",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(Vector2(0.62, 0.82),
                             parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.interact.alias]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def aliasshoot():
            if not _button.active:
                Keyboard.interact.alias = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changeshoot(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.interact.alias = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.interact.alias].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def pause():
        _sprite = sprite(
            name="pausesprite",
            path=PATH / "assets" / "menu" / "keybinds" / "pause.png",
            manager=game
        )

        _sprite.set_position(
            Vector2(0.28, 1.), parent=keybind_menu.get_sprite("panel"))
        _sprite.set_scale(Vector2(4.0, 4.0))

        return _sprite

    @keybind_menu.get_sprite("panel").add_sprite
    def pausekey():
        _button = Button(
            name="pausekey",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(
            Vector2(0.54, 1.), parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.pause.key]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def keypause():
            if not _button.active:
                Keyboard.pause.key = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changepause(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.pause.key = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.pause.key].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def pausealias():
        _button = Button(
            name="pausealias",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(
            Vector2(0.62, 1.), parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.pause.alias]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def aliaspause():
            if not _button.active:
                Keyboard.pause.alias = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changepause(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.pause.alias = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.pause.alias].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def endturn():
        _sprite = sprite(
            name="endturnsprite",
            path=PATH / "assets" / "menu" / "keybinds" / "endturn.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.28, 1.18),
                             parent=keybind_menu.get_sprite("panel"))
        _sprite.set_scale(Vector2(4.0, 4.0))

        return _sprite

    @keybind_menu.get_sprite("panel").add_sprite
    def endturnkey():
        _button = Button(
            name="endturnkey",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(Vector2(0.54, 1.18),
                             parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.end_turn.key]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def keyendturn():
            if not _button.active:
                Keyboard.end_turn.key = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changeendturn(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.end_turn.key = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.end_turn.key].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    @keybind_menu.get_sprite("panel").add_sprite
    def endturnalias():
        _button = Button(
            name="endturnalias",
            path=PATH / "assets" / "menu" / "keybinds" / "button_keybind.png",
            manager=game
        )

        _button.set_position(Vector2(0.62, 1.18),
                             parent=keybind_menu.get_sprite("panel"))
        _button.set_scale(Vector2(4.0, 4.0))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "keybinds" / "keybinds.png", (28, 28))
        _button.spritesheet.config(_button.image.get_size())
        _button.image = _button.spritesheet[Keyboard.end_turn.alias]
        _button.active = False

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def aliasendturn():
            if not _button.active:
                Keyboard.end_turn.alias = -1
                _button.image = _button.spritesheet[-1]
                _button.active = True
                for sprite in keybind_menu.get_sprite("panel").sprites:
                    if type(sprite) == Button and hasattr(sprite, "active") and sprite is not _button:
                        sprite.active = False
            else:
                _button.active = False
                Keyboard.save(PATH)

        @_button.Event(pygame.KEYDOWN)
        def changeendturn(event):
            if _button.active:
                if event.key in sprite_sheet.dico.keys() and not Keyboard.key_used(event.key):
                    _button.active = False
                    Keyboard.end_turn.alias = event.key
                    _button.image = _button.spritesheet[event.key]
                    Keyboard.save(PATH)
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key.wav", volume=4)
                else:
                    MixeurAudio.play_effect(
                        PATH / "assets" / "sound" / "button-key-fail.wav", volume=4)

        @_button.Event(None)
        def animate():
            _button.image = _button.spritesheet[Keyboard.end_turn.alias].copy()
            if _button.active:
                _button.image.fill(
                    (255, 255, 255, 200 + 55*sin(pygame.time.get_ticks()/200)), special_flags=BLEND_RGBA_MULT)

        return _button

    # endregion

    # region Play menu
    @play_menu.add_sprite
    def go_backbutton():
        _button = Button(
            name="gobackbutton",
            path=PATH / "assets" / "menu" / "play" / "gobackbutton3.png",
            manager=game
        )

        _button.set_position(Vector2(0.18, 0.85))
        _button.set_scale(Vector2(2.0, 2.0))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def go_back():
            game.actual_menu = play_menu.get_parent()

        return _button

    @play_menu.add_sprite
    def title():
        _sprite = sprite(
            name="title",
            path=PATH / "assets" / "menu" / "play" / "team-choice.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.5, 0.18))
        _sprite.set_scale(Vector2(3.0, 3.0))

        return _sprite

    @play_menu.add_sprite
    def chain1():
        _sprite = sprite(
            name="chain1",
            path=PATH / "assets" / "menu" / "play" / "chain.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.33, 0.05))
        _sprite.set_scale(Vector2(2.0, 2.0))

        return _sprite

    @play_menu.add_sprite
    def chain2():
        _sprite = sprite(
            name="chain2",
            path=PATH / "assets" / "menu" / "play" / "chain.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.67, 0.05))
        _sprite.set_scale(Vector2(2.0, 2.0))

        return _sprite

    @play_menu.add_sprite
    def play_button():
        _button = Button(
            name="playbutton",
            path=PATH / "assets" / "menu" / "play" / "playbutton.png",
            manager=game,
        )

        _button.set_position(Vector2(0.5, 0.5))
        _button.set_scale(Vector2(3.0, 3.0))

        @_button.on_click(PATH / "assets" / "sound" / "explosion.wav")
        def start():
            for sprite in play_menu.sprites():
                sprite.isactive = not sprite.isactive

        @_button.Event(pygame.KEYDOWN)
        def start(event):
            if event.key == Keyboard.interact.key:
                MixeurAudio.play_effect(
                    PATH / "assets" / "sound" / "explosion.wav")
                for sprite in play_menu.sprites():
                    sprite.isactive = not sprite.isactive

        return _button

    @play_menu.add_sprite
    def start_explosion():
        manager = animation_Manager()
        explosion = sprite_sheet(
            PATH / "assets" / "explosion" / "explosion-5.png", (192, 192))
        explosion.config((1920, 1080))

        @explosion.add_on_end
        def func():
            GAME.start_partie(str(play_menu.get_sprite("plateform1").cycle), str(
                play_menu.get_sprite("plateform2").cycle))

        manager.add_annimation("explosion", explosion, 1)

        manager.load("explosion")

        _button = animated_sprite(
            name="explosion",
            manager=game,
            animation_manager=manager,
            isactive=False
        )

        _button.set_position(Vector2(0.5, 0.5))

        return _button

    @play_menu.add_sprite
    def plateform1():
        _button = Button(
            name="plateform1",
            path=PATH / "assets" / "menu" / "play" / "plateform_button.png",
            manager=game
        )

        _button.set_position(Vector2(0.27, 0.65))
        _button.set_scale(Vector2(1.5, 1.5))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "play" / "plateform.png", (288, 96))
        _button.spritesheet.config(_button.image.get_size())
        _button.cycle = cycle("perso_1", "perso_2", "perso_3", "perso_4")
        _button.image = _button.spritesheet[int(_button.cycle)]

        @_button.Event(None)
        def change_name1():
            _button.image = _button.spritesheet[int(_button.cycle)]

        return _button

    @play_menu.add_sprite
    def name_arrow1():
        _button = Button(
            name="namearrow1",
            path=PATH / "assets" / "menu" / "play" / "leftarrow.png",
            manager=game
        )

        _button.set_position(Vector2(0.15, 0.63))
        _button.set_scale(Vector2(3.0, 3.0))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def left_change1():
            _sprt = play_menu.get_sprite("plateform1")
            _sprt.cycle -= 1
            if int(_sprt.cycle) == int(play_menu.get_sprite("plateform2").cycle):
                _sprt.cycle -= 1
            _sprt2 = play_menu.get_sprite("perso1")
            _sprt2.manager.load(str(_sprt.cycle))
            _pos = Vector2(*_sprt.rect.center)
            _pos.y -= _sprt2.manager.actual_surface.get_height()
            _sprt2.set_position(_pos, TopLeft=False)

        return _button

    @play_menu.add_sprite
    def name_arrow2():
        _button = Button(
            name="namearrow2",
            path=PATH / "assets" / "menu" / "play" / "rightarrow.png",
            manager=game
        )

        _button.set_position(Vector2(0.39, 0.63))
        _button.set_scale(Vector2(3.0, 3.0))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def right_change1():
            _sprt = play_menu.get_sprite("plateform1")
            _sprt.cycle += 1
            if int(_sprt.cycle) == int(play_menu.get_sprite("plateform2").cycle):
                _sprt.cycle += 1
            _sprt2 = play_menu.get_sprite("perso1")
            _sprt2.manager.load(str(_sprt.cycle))
            _pos = Vector2(*_sprt.rect.center)
            _pos.y -= _sprt2.manager.actual_surface.get_height()
            _sprt2.set_position(_pos, TopLeft=False)

        return _button

    @play_menu.add_sprite
    def perso1():
        manager = animation_Manager()
        spritesheet1 = sprite_sheet(
            PATH / "assets" / "perso" / "perso_1" / "idle.png", (24, 28))
        spritesheet1.config((120, 135))
        spritesheet2 = sprite_sheet(
            PATH / "assets" / "perso" / "perso_2" / "idle.png", (42, 29))
        spritesheet2.config((210, 145))
        spritesheet3 = sprite_sheet(
            PATH / "assets" / "perso" / "perso_3" / "idle.png", (24, 28))
        spritesheet3.config((120, 135))
        spritesheet4 = sprite_sheet(
            PATH / "assets" / "perso" / "perso_4" / "idle.png", (31, 28))
        spritesheet4.config((155, 135))
        manager.add_annimation("perso_1", spritesheet1, 10)
        manager.add_annimation("perso_2", spritesheet2, 7)
        manager.add_annimation("perso_3", spritesheet3, 7)
        manager.add_annimation("perso_4", spritesheet4, 7)
        manager.load("perso_1")

        _button = animated_sprite(
            name="perso1",
            manager=game,
            animation_manager=manager
        )

        _button.set_position(Vector2(0.27, 0.5248))

        return _button

    @play_menu.add_sprite
    def plateform2():
        _button = Button(
            name="plateform2",
            path=PATH / "assets" / "menu" / "play" / "plateform_button.png",
            manager=game
        )

        _button.set_position(Vector2(0.73, 0.65))
        _button.set_scale(Vector2(1.5, 1.5))

        _button.spritesheet = sprite_sheet(
            PATH / "assets" / "menu" / "play" / "plateform.png", (288, 96))
        _button.spritesheet.config(_button.image.get_size())
        _button.cycle = cycle("perso_1", "perso_2",
                              "perso_3", "perso_4", index=1)
        _button.image = _button.spritesheet[int(_button.cycle)]

        @_button.Event(None)
        def change_name2():
            _button.image = _button.spritesheet[int(_button.cycle)]

        return _button

    @play_menu.add_sprite
    def name_arrow3():
        _button = Button(
            name="namearrow3",
            path=PATH / "assets" / "menu" / "play" / "leftarrow.png",
            manager=game
        )

        _button.set_position(Vector2(0.61, 0.63))
        _button.set_scale(Vector2(3.0, 3.0))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def left_change2():
            _sprt = play_menu.get_sprite("plateform2")
            _sprt.cycle -= 1
            if int(_sprt.cycle) == int(play_menu.get_sprite("plateform1").cycle):
                _sprt.cycle -= 1
            _sprt2 = play_menu.get_sprite("perso2")
            _sprt2.manager.load(str(_sprt.cycle))
            _pos = Vector2(*_sprt.rect.center)
            _pos.y -= _sprt2.manager.actual_surface.get_height()
            _sprt2.set_position(_pos, TopLeft=False)

        return _button

    @play_menu.add_sprite
    def name_arrow4():
        _button = Button(
            name="namearrow4",
            path=PATH / "assets" / "menu" / "play" / "rightarrow.png",
            manager=game
        )

        _button.set_position(Vector2(0.85, 0.63))
        _button.set_scale(Vector2(3.0, 3.0))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def right_change2():
            _sprt = play_menu.get_sprite("plateform2")
            _sprt.cycle += 1
            if int(_sprt.cycle) == int(play_menu.get_sprite("plateform1").cycle):
                _sprt.cycle += 1
            _sprt2 = play_menu.get_sprite("perso2")
            _sprt2.manager.load(str(_sprt.cycle))
            _pos = Vector2(*_sprt.rect.center)
            _pos.y -= _sprt2.manager.actual_surface.get_height()
            _sprt2.set_position(_pos, TopLeft=False)

        return _button

    @play_menu.add_sprite
    def perso2():
        manager = animation_Manager()
        spritesheet1 = sprite_sheet(
            PATH / "assets" / "perso" / "perso_1" / "idle.png", (24, 28))
        spritesheet1.config((120, 135))
        spritesheet2 = sprite_sheet(
            PATH / "assets" / "perso" / "perso_2" / "idle.png", (42, 29))
        spritesheet2.config((210, 145))
        spritesheet3 = sprite_sheet(
            PATH / "assets" / "perso" / "perso_3" / "idle.png", (24, 28))
        spritesheet3.config((120, 135))
        spritesheet4 = sprite_sheet(
            PATH / "assets" / "perso" / "perso_4" / "idle.png", (31, 28))
        spritesheet4.config((155, 135))
        manager.add_annimation("perso_1", spritesheet1, 10)
        manager.add_annimation("perso_2", spritesheet2, 7)
        manager.add_annimation("perso_3", spritesheet3, 7)
        manager.add_annimation("perso_4", spritesheet4, 7)
        manager.load("perso_2")

        _button = animated_sprite(
            name="perso2",
            manager=game,
            animation_manager=manager
        )

        _button.set_position(Vector2(0.73, 0.5248))

        return _button

    # endregion

    # region Rules menu

    @rules_menu.add_sprite
    def board():
        _sprite = sprite(
            name="board",
            path=PATH / "assets" / "menu" / "rules" / "brownboard.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.5, 0.5))
        _sprite.set_scale(Vector2(2.03, 1.83))

        return _sprite

    @rules_menu.add_sprite
    def gobackbutton():
        _button = Button(
            name="gobackbutton",
            path=PATH / "assets" / "menu" / "rules" / "goback.png",
            manager=game
        )

        _button.set_position(Vector2(0.18, 0.85))
        _button.set_scale(Vector2(5.1, 5.1))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def goback():
            game.actual_menu = rules_menu.get_parent()

        return _button

    @rules_menu.add_sprite
    def title1():
        _sprite = sprite(
            name="title1",
            path=PATH / "assets" / "menu" / "rules" / "team.png",
            manager=game
        )

        _sprite.set_position(Vector2(0.5, 0.1))
        _sprite.set_scale(Vector2(5.1, 5.1))

        return _sprite

    @rules_menu.add_sprite
    def text1():
        _text = textZone(
            name="text1",
            size=Vector2(200, 200),
            manager=game,
            text_color="black"
        )

        _text.set_position(Vector2(0.5, 0.3))
        _text.set_text(
            "You will play 2 characters that you\nwill chose before the game starts !")
        _text.fit_to_size()
        _text.render()

        @_text.Event(None)
        def update():
            print(_text.rect, _text.get_size(), _text.FONT)

        return _text

    # endregion

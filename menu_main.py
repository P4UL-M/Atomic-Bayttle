import pygame
from pygame.locals import *
from pygame_easy_menu import *
from pygame_easy_menu.tools import *
from tools.tools import MixeurAudio, animation_Manager, sprite_sheet, cycle
import pathlib

GAME = None
CAMERA = None

PATH = pathlib.Path(__file__).parent
game = None

class CursorButton(Button,sprite):
    def __init__(self,name,path,manager,isactive=True,layer=0, pos:Vector2=Vector2(0,0)):
        super().__init__(name, path,manager, isactive, layer)
        self.cursor_position = pos

class animated_sprite(sprite): # class without surface set and annimated
    def __init__(self,name,manager,animation_manager,isactive=True,layer=0, pos:Vector2=Vector2(0,0)):
        super(sprite, self).__init__()
        self.name = name
        self.layer = layer
        self.isactive = isactive
        self._manager = manager
        self.manager = animation_manager
        
        self.handles = []

        self.rect = self.image.get_rect(topleft=(0,0))
        self.initial_size = Vector2(self.image.get_width(),self.image.get_height())

    @property
    def image(self):
        return self.manager.surface

    def set_scale(self, sca: Vector2, center=True): ...

def setup_manager():
    global game
    CAMERA._off_screen = pygame.Surface((1920,1080),flags=HWSURFACE + HWACCEL)
    CAMERA.HUD = False
    CAMERA.zoom = 1
    CAMERA.maximise = False
    MixeurAudio.set_musique(path=PATH / "assets" / "music" / "main-loop.wav")
    pygame.mouse.set_visible(True)

    game = Menu_Manager(name="Atomic Bay'ttle", window=CAMERA._off_screen, background=PATH / "assets" / "menu" / "background_sheet.png")
    game.play_effect = MixeurAudio.play_effect
    game.running = True

    principal = Menu("Principal",game, childs=["Settings", "Play"])
    settings_menu = Menu("Settings",game, parent="Principal", childs="Keybinds")
    keybind_menu = Menu("Keybinds",game, parent="Settings")
    play_menu = Menu("Play",game, parent="Principal")


    #region Principal menu
    @principal.set_setup
    def princ_setup():
        MixeurAudio.load(PATH)

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
            pass

        return _button

    @principal.add_sprite
    def settings_button():
        _button=Button(
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
        _button=Button(
            name="play",
            path=PATH / "assets" / "menu" / "principal" / "playbutton.png",
            manager=game
            )
        
        _button.set_position(Vector2(0.5, 0.4))
        _button.set_scale(Vector2(0.56, 0.56))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def play():
            game.actual_menu = principal.get_child("Play")

        return _button

    @principal.add_sprite
    def title_sprite():
        _button=sprite(
            name="title",
            path=PATH / "assets" / "menu" / "principal" / "atomic_bay'ttle.png",
            manager=game
            )

        _button.set_position(Vector2(0.5, 0.17))
        _button.set_scale(Vector2(10.0, 9.0))

        return _button

    game.actual_menu = principal

    #endregion

    #region Settings menu

    @settings_menu.set_setup
    def setup():
        cursor_effects = settings_menu.get_sprite("effects_cursor")
        effects_sprite = settings_menu.get_sprite(f"effects_volume{int(MixeurAudio.volume_effect*10)}")
        _pos = Vector2(*effects_sprite.rect.center)
        _offset = effects_sprite.cursor_position
        cursor_effects.set_position(_pos + _offset)

        cursor_music = settings_menu.get_sprite("music_cursor")
        music_sprite = settings_menu.get_sprite(f"music_volume{int(MixeurAudio.volume_musique*10)}")
        _pos = Vector2(*music_sprite.rect.center)
        _offset = music_sprite.cursor_position
        cursor_music.set_position(_pos + _offset)

    @settings_menu.add_sprite
    def settings_bg():
        _button=Button(
            name='settings_bg',
            path=PATH / "assets" / "menu" / "settings" / "green_board.png",
            manager=game
            )
        
        _button.set_position(Vector2(0.5,0.5))
        _button.set_scale(Vector2(7.5,7.5))

        return _button

    @settings_menu.add_sprite
    def goback_button():
        _button=Button(
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

    #region volume_button
    @settings_menu.add_sprite
    def effects_volume0():
        _button=CursorButton(
            name="effects_volume0",
            path=PATH / "assets" / "menu" / "settings" / "leftslide0.png",
            manager=game,
            pos=Vector2(3,0)
            )
        
        _button.set_scale(Vector2(4.58,4.58))
        _button.set_position(Vector2(0.2464,0.575))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects0():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume1():
        _button=CursorButton(
            name="effects_volume1",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.2687, 0.575))
        _button.set_scale(Vector2(4.07,4.58))
        
        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects1():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.1
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume2():
        _button=CursorButton(
            name="effects_volume2",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.2895, 0.575))
        _button.set_scale(Vector2(4.07,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects2():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.2
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume3():
        _button=CursorButton(
            name="effects_volume3",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.3104, 0.575))
        _button.set_scale(Vector2(4.07,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects3():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.3
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume4():
        _button=CursorButton(
            name="effects_volume4",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.3312, 0.575))
        _button.set_scale(Vector2(4.07,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects4():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.4
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume5():
        _button=CursorButton(
            name="effects_volume5",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.3520, 0.575))
        _button.set_scale(Vector2(4.07,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects5():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.5
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume6():
        _button=CursorButton(
            name="effects_volume6",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.3729, 0.575))
        _button.set_scale(Vector2(4.07,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects6():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.6
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume7():
        _button=CursorButton(
            name="effects_volume7",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.3937, 0.575))
        _button.set_scale(Vector2(4.07,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects7():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.7
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume8():
        _button=CursorButton(
            name="effects_volume8",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.4145, 0.575))
        _button.set_scale(Vector2(4.07,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects8():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.8
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume9():
        _button=CursorButton(
            name="effects_volume9",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.4353, 0.575))
        _button.set_scale(Vector2(4.07,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects9():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 0.9
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def effects_volume10():
        _button=CursorButton(
            name="effects_volume10",
            path=PATH / "assets" / "menu" / "settings" / "rightslide0.png",
            manager=game,
            pos=Vector2(-3,0)
            )

        _button.set_position(Vector2(0.457, 0.575))
        _button.set_scale(Vector2(4.58,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_effects10():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("effects_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_effect = 1.0
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume0():
        _button=CursorButton(
            name="music_volume0",
            path=PATH / "assets" / "menu" / "settings" / "leftslide0.png",
            manager=game,
            pos=Vector2(3,0)
            )
        
        _button.set_scale(Vector2(4.58,4.58))
        _button.set_position(Vector2(0.540,0.575))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music0():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume1():
        _button=CursorButton(
            name="music_volume1",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.5624, 0.575))
        _button.set_scale(Vector2(4.07,4.58))
        
        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music1():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.1
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume2():
        _button=CursorButton(
            name="music_volume2",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.5833, 0.575))
        _button.set_scale(Vector2(4.07,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music2():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.2
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume3():
        _button=CursorButton(
            name="music_volume3",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.6041, 0.575))
        _button.set_scale(Vector2(4.07,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music3():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.3
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume4():
        _button=CursorButton(
            name="music_volume4",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.6249, 0.575))
        _button.set_scale(Vector2(4.07,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music4():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.4
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume5():
        _button=CursorButton(
            name="music_volume5",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.6458, 0.575))
        _button.set_scale(Vector2(4.07,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music5():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.5
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume6():
        _button=CursorButton(
            name="music_volume6",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.6666, 0.575))
        _button.set_scale(Vector2(4.07,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music6():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.6
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume7():
        _button=CursorButton(
            name="music_volume7",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.6874, 0.575))
        _button.set_scale(Vector2(4.07,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music7():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.7
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume8():
        _button=CursorButton(
            name="music_volume8",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.7083, 0.575))
        _button.set_scale(Vector2(4.07,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music8():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.8
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume9():
        _button=CursorButton(
            name="music_volume9",
            path=PATH / "assets" / "menu" / "settings" / "middleslide0.png",
            manager=game
            )

        _button.set_position(Vector2(0.7291, 0.575))
        _button.set_scale(Vector2(4.07,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music9():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 0.9
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    @settings_menu.add_sprite
    def music_volume10():
        _button=CursorButton(
            name="music_volume10",
            path=PATH / "assets" / "menu" / "settings" / "rightslide0.png",
            manager=game,
            pos=Vector2(-3,0)
            )

        _button.set_position(Vector2(0.751, 0.575))
        _button.set_scale(Vector2(4.58,4.58))

        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def set_music10():
            _pos = Vector2(*_button.rect.center)+ _button.cursor_position
            cursor = settings_menu.get_sprite("music_cursor")
            cursor.set_position(_pos)
            MixeurAudio.volume_musique = 1
            MixeurAudio.update_volume()
            MixeurAudio.save(PATH)

        return _button

    #endregion

    @settings_menu.add_sprite
    def effects_cursor():
        _button=Button(
            name="effects_cursor",
            path=PATH / "assets" / "menu" / "settings" / "cursor.png",
            manager=game
            )

        _button.set_scale(Vector2(4.58,4.58))

        return _button

    @settings_menu.add_sprite
    def music_cursor():
        _button=Button(
            name="music_cursor",
            path=PATH / "assets" / "menu" / "settings" / "cursor.png",
            manager=game
            )

        _button.set_scale(Vector2(4.58,4.58))

        return _button

    @settings_menu.add_sprite
    def effects_button():
        _button=sprite(
            name="effects",
            path=PATH / "assets" / "menu" / "settings" / "effectsbutton.png",
            manager=game
            )
        
        _button.set_position(Vector2(0.353,0.50))
        _button.set_scale(Vector2(2.6,2.6))

        return _button

    @settings_menu.add_sprite
    def music_button():
        _button=sprite(
            name="effects",
            path=PATH / "assets" / "menu" / "settings" / "musicbutton.png",
            manager=game
            )
        
        _button.set_position(Vector2(0.647,0.50))
        _button.set_scale(Vector2(2.6,2.6))

        return _button

    @settings_menu.add_sprite
    def chain8():
        _button=sprite(
            name="chain8",
            path = PATH / "assets" / "menu" / "settings" / "chain.png",
            manager=game
            )

        _button.set_position(Vector2(0.75, 0.42))
        _button.set_scale(Vector2(2.0,2.0))

        return _button

    @settings_menu.add_sprite
    def chain7():
        _button=sprite(
            name="chain6",
            path=PATH / "assets" / "menu" / "settings" / "chain.png",
            manager=game
            )

        _button.set_position(Vector2(0.544,0.42))
        _button.set_scale(Vector2(2.0,2.0))

        return _button

    @settings_menu.add_sprite
    def chain6():
        _button=sprite(
            name="chain6",
            path=PATH / "assets" / "menu" / "settings" / "chain.png",
            manager=game
            )

        _button.set_position(Vector2(0.25,0.42))
        _button.set_scale(Vector2(2.0,2.0))

        return _button

    @settings_menu.add_sprite
    def chain5():
        _button=sprite(
            name="chain5",
            path=PATH / "assets" / "menu" / "settings" / "chain.png",
            manager=game
            )

        _button.set_position(Vector2(0.456,0.42))
        _button.set_scale(Vector2(2.0,2.0))

        return _button

    @settings_menu.add_sprite
    def volume_button():
        _button=sprite(
            name="volume",
            path=PATH / "assets" / "menu" / "settings" / "volumebutton.png",
            manager=game
            )

        _button.set_position(Vector2(0.5, 0.36))
        _button.set_scale(Vector2(4.0,4.0))

        return _button

    @settings_menu.add_sprite
    def chain3():
        _button=sprite(
            name="chain3",
            path=PATH / "assets" / "menu" / "settings" / "chain.png",
            manager=game
            )

        _button.set_position(Vector2(0.26,0.27))
        _button.set_scale(Vector2(2.0, 2.0))

        return _button

    @settings_menu.add_sprite
    def chain4():
        _button=sprite(
            name="chain4",
            path=PATH / "assets" / "menu" / "settings" / "chain.png",
            manager=game
            )

        _button.set_position(Vector2(0.74,0.27))
        _button.set_scale(Vector2(2.0, 2.0))

        return _button

    @settings_menu.add_sprite
    def settings_title():
        _button=sprite(
            name="title",
            path=PATH / "assets" / "menu" / "settings" / "settingsbutton2.png",
            manager=game
            )

        _button.set_position(Vector2(0.5, 0.18))
        _button.set_scale(Vector2(4.0,4.0))

        return _button

    @settings_menu.add_sprite
    def chain1():
        _button=sprite(
            name="chain1",
            path=PATH / "assets" / "menu" / "settings" / "smallchain.png",
            manager=game
            )

        _button.set_position(Vector2(0.26,0.085))
        _button.set_scale(Vector2(2.0, 2.0))

        return _button

    @settings_menu.add_sprite
    def chain2():
        _button=sprite(
            name="chain2",
            path=PATH / "assets" / "menu" / "settings" / "smallchain.png",
            manager=game
            )
        
        _button.set_position(Vector2(0.74, 0.085))
        _button.set_scale(Vector2(2.0,2.0))

        return _button

    @settings_menu.add_sprite
    def keybinds_button():
        _button=Button(
            name="keybinds_button",
            path=PATH / "assets" / "menu" / "settings" / "keybindsbutton.png",
            manager=game
            )

        _button.set_position(Vector2(0.5,0.7))
        _button.set_scale(Vector2(4.0,3.0))
        
        @_button.on_click(PATH / "assets" / "sound" / "button-menu.wav")
        def keybinds_change():
            game.actual_menu = settings_menu.get_child("Keybinds")

        return _button

    #endregion

    #region Keybinds_menu

    @keybind_menu.add_sprite
    def keybind_bg():
        _button=sprite(
            name="keybind_bg",
            path=PATH / "assets" / "menu" / "keybinds" / "yellow_board.png",
            manager=game
            )

        _button.set_position(Vector2(0.5,0.5))
        _button.set_scale(Vector2(7.0,7.0))

        return _button
        
    @keybind_menu.add_sprite
    def goback():
        _button=Button(
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
    def movebutton():
        _button=Button(
            name="movebutton",
            path=PATH / "assets" / "menu" / "keybinds" / "move.png",
            manager=game
            )

        _button.set_position(Vector2(0.5,0.18))
        _button.set_scale(Vector2(4.0,4.0))

        return _button

    #endregion

    #region Play menu
    @play_menu.add_sprite
    def go_backbutton():
        _button=Button(
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
        _sprite=sprite(
            name="title",
            path=PATH / "assets" / "menu" / "play" / "team-choice.png",
            manager=game
            )

        _sprite.set_position(Vector2(0.5,0.18))
        _sprite.set_scale(Vector2(0.7,0.7))

        return _sprite

    @play_menu.add_sprite
    def chain1():
        _sprite=sprite(
            name="chain1",
            path=PATH / "assets" / "menu" / "play" / "chain.png",
            manager=game
            )

        _sprite.set_position(Vector2(0.38,0.08))
        _sprite.set_scale(Vector2(2.0,2.0))

        return _sprite

    @play_menu.add_sprite
    def play_button():
        _button=Button(
            name="playbutton",
            path=PATH / "assets" / "menu" / "play" / "playbutton.png",
            manager=game
            )
        
        _button.set_position(Vector2(0.5, 0.5))
        _button.set_scale(Vector2(3.0,3.0))

        @_button.on_click()
        def start():
            GAME.start_partie(str(play_menu.get_sprite("plateform1").cycle))

        return _button

    @play_menu.add_sprite
    def plateform1():
        _button=Button(
            name="plateform1",
            path=PATH / "assets" / "menu" / "play" / "plateform_button.png",
            manager=game
            )

        _button.set_position(Vector2(0.27,0.65))
        _button.set_scale(Vector2(1.5,1.5))

        _button.spritesheet = sprite_sheet(PATH / "assets" / "menu" / "play" / "plateform.png", (288,96))
        _button.spritesheet.config(_button.image.get_size())
        _button.cycle = cycle("perso_1", "perso_2", "perso_3", "perso_4")
        _button.image = _button.spritesheet[int(_button.cycle)]

        @_button.Event(None)
        def change_name1():
            _button.image = _button.spritesheet[int(_button.cycle)]

        return _button

    @play_menu.add_sprite
    def name_arrow1():
        _button=Button(
            name="namearrow1",
            path=PATH / "assets" / "menu" / "play" / "leftarrow.png",
            manager=game
            )

        _button.set_position(Vector2(0.15,0.63))
        _button.set_scale(Vector2(3.0,3.0))

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
            _sprt2.set_position(_pos,TopLeft=False)

        return _button
        
    @play_menu.add_sprite
    def name_arrow2():
        _button=Button(
            name="namearrow2",
            path=PATH / "assets" / "menu" / "play" / "rightarrow.png",
            manager=game
            )

        _button.set_position(Vector2(0.39,0.63))
        _button.set_scale(Vector2(3.0,3.0))

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
            _sprt2.set_position(_pos,TopLeft=False)

        return _button

    @play_menu.add_sprite
    def perso1():
        manager = animation_Manager()
        spritesheet1 = sprite_sheet(PATH / "assets" / "perso" / "perso_1" / "spritesheet1.png", (24,28))
        spritesheet1.config((120,135))
        spritesheet2 = sprite_sheet(PATH / "assets" / "perso" / "perso_2" / "spritesheet2.png", (42,29))
        spritesheet2.config((210,145))
        spritesheet3 = sprite_sheet(PATH / "assets" / "perso" / "perso_3" / "spritesheet3.png", (24,28))
        spritesheet3.config((120,135))
        spritesheet4 = sprite_sheet(PATH / "assets" / "perso" / "perso_4" / "spritesheet4.png", (31,28))
        spritesheet4.config((155,135))
        manager.add_annimation("perso_1",spritesheet1,10)
        manager.add_annimation("perso_2",spritesheet2,7)
        manager.add_annimation("perso_3",spritesheet3,7)
        manager.add_annimation("perso_4",spritesheet4,7)
        manager.load("perso_1")

        _button=animated_sprite(
            name="perso1",
            manager = game,
            animation_manager=manager
            )
        
        _button.set_position(Vector2(0.27,0.5248))
        
        return _button

    @play_menu.add_sprite
    def plateform2():
        _button=Button(
            name="plateform2",
            path=PATH / "assets" / "menu" / "play" / "plateform_button.png",
            manager=game
            )

        _button.set_position(Vector2(0.73,0.65))
        _button.set_scale(Vector2(1.5,1.5))

        _button.spritesheet = sprite_sheet(PATH / "assets" / "menu" / "play" / "plateform.png", (288,96))
        _button.spritesheet.config(_button.image.get_size())
        _button.cycle = cycle("perso_1", "perso_2", "perso_3", "perso_4", index=1)
        _button.image = _button.spritesheet[int(_button.cycle)]

        @_button.Event(None)
        def change_name2():
            _button.image = _button.spritesheet[int(_button.cycle)]

        return _button

    @play_menu.add_sprite
    def name_arrow3():
        _button=Button(
            name="namearrow3",
            path=PATH / "assets" / "menu" / "play" / "leftarrow.png",
            manager=game
            )

        _button.set_position(Vector2(0.61,0.63))
        _button.set_scale(Vector2(3.0,3.0))

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
            _sprt2.set_position(_pos,TopLeft=False)

        return _button
        
    @play_menu.add_sprite
    def name_arrow4():
        _button=Button(
            name="namearrow4",
            path=PATH / "assets" / "menu" / "play" / "rightarrow.png",
            manager=game
            )

        _button.set_position(Vector2(0.85,0.63))
        _button.set_scale(Vector2(3.0,3.0))

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
            _sprt2.set_position(_pos,TopLeft=False)

        return _button

    @play_menu.add_sprite
    def perso2():
        manager = animation_Manager()
        spritesheet1 = sprite_sheet(PATH / "assets" / "perso" / "perso_1" / "spritesheet1.png", (24,28))
        spritesheet1.config((120,135))
        spritesheet2 = sprite_sheet(PATH / "assets" / "perso" / "perso_2" / "spritesheet2.png", (42,29))
        spritesheet2.config((210,145))
        spritesheet3 = sprite_sheet(PATH / "assets" / "perso" / "perso_3" / "spritesheet3.png", (24,28))
        spritesheet3.config((120,135))
        spritesheet4 = sprite_sheet(PATH / "assets" / "perso" / "perso_4" / "spritesheet4.png", (31,28))
        spritesheet4.config((155,135))
        manager.add_annimation("perso_1",spritesheet1,10)
        manager.add_annimation("perso_2",spritesheet2,7)
        manager.add_annimation("perso_3",spritesheet3,7)
        manager.add_annimation("perso_4",spritesheet4,7)
        manager.load("perso_2")

        _button=animated_sprite(
            name="perso2",
            manager = game,
            animation_manager=manager
            )
        
        _button.set_position(Vector2(0.73,0.5248))
        
        return _button

    #endregion
import pygame
from tools.tools import Keyboard, MixeurAudio,Axis
import tools.generate_music as gn

y = Axis()
music = False
GAME = None
CAMERA = None

def loop(PATH):
    global music
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                GAME.running = False    
            case pygame.MOUSEBUTTONDOWN if event.button == 1:
                pygame.draw.circle(GAME.surf, (0,0,0,0), pygame.mouse.get_pos(), 50)
        
                MixeurAudio.play_effect(PATH / "assets" / "sound" / "button-menu.wav")
                MixeurAudio.music_factor.value += 0.05
                if not music:
                    music = True
                    MixeurAudio.stop("music")
            case pygame.MOUSEBUTTONDOWN if event.button ==3:
                MixeurAudio.gn.reset()
            case pygame.MOUSEWHEEL:
                CAMERA.zoom += event.y*GAME.serialized*0.05
        
    state = pygame.key.get_pressed()

    if state[pygame.K_z]:
        CAMERA.y -= 0.05*GAME.serialized/CAMERA.zoom
    if state[pygame.K_s]:
        CAMERA.y += 0.05*GAME.serialized/CAMERA.zoom
    if state[pygame.K_d]:
        CAMERA.x += 0.05*GAME.serialized/CAMERA.zoom
    if state[pygame.K_q]:
        CAMERA.x -= 0.05*GAME.serialized/CAMERA.zoom

    y.update(Keyboard.up.is_pressed,Keyboard.down.is_pressed)

    if music:
        MixeurAudio.update_musique()
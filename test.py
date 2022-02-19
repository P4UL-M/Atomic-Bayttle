import pygame
from tools.tools import Keyboard, MixeurAudio,Axis

y = Axis()
music = False
GAME = None
CAMERA = None

def loop(PATH):
    global music
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            GAME.running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                MixeurAudio.play_effect(PATH / "assets" / "sound" / "button-menu.wav")
                MixeurAudio.music_factor.value += 0.05
                if not music:
                    music = True
                    MixeurAudio.stop("music")
        if event.type == pygame.MOUSEWHEEL:
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

        
    surf = pygame.Surface((10,10))
    surf.fill((255,100,0))

    CAMERA._off_screen.blit(surf,pygame.mouse.get_pos())

    y.update(Keyboard.up.is_pressed,Keyboard.down.is_pressed)

    if music: MixeurAudio.update_musique()
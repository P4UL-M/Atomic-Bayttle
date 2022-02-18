import pygame
from tools.tools import Keyboard, MixeurAudio,Axis

y = Axis()
music = False

def loop(PATH):
    global music
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            MixeurAudio.play_effect(PATH / "assets" / "sound" / "button-menu.wav")
            MixeurAudio.music_factor.value += 0.05
            if not music:
                music = True
                MixeurAudio.stop("music")

    y.update(Keyboard.up.is_pressed,Keyboard.down.is_pressed)
    print(y.value)

    if music: MixeurAudio.update_musique()
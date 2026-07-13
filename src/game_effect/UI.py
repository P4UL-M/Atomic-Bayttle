"""
Atomic Bay'ttle
Paul Mairesse, Axel Loones, Louis Le Meilleur, Joseph Bénard, Théo de Aranjo
This file contain the definition of the elements of the HUD of the game
"""
from src.tools.tools import sprite_sheet
from src.tools.constant import PATH
import pygame

SP = sprite_sheet(PATH / "assets" / "UI" / "numbers.png", (10, 11))
SP.dico = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, "%": 10}
HEARTS = sprite_sheet(PATH / "assets" / "UI" / "hearts.png", (10, 9))
HEARTS.dico = {True: 0, False: 1}
_DIGIT_CACHE = {}
_HEART_CACHE = {}


class digit(pygame.sprite.Sprite):
    def __init__(self, nb, size=1) -> None:
        super().__init__()
        key = (nb, size)
        if key not in _DIGIT_CACHE:
            _DIGIT_CACHE[key] = pygame.transform.scale(
                SP[nb], (int(10 * size), int(11 * size))
            )
        self.image = _DIGIT_CACHE[key]
        self.rect = self.image.get_rect()


class heart(pygame.sprite.Sprite):
    def __init__(self, life: bool, size=1) -> None:
        super().__init__()
        key = (life, size)
        if key not in _HEART_CACHE:
            _HEART_CACHE[key] = pygame.transform.scale(
                HEARTS[life], (int(10 * size), int(9 * size))
            )
        self.image = _HEART_CACHE[key]
        self.rect = self.image.get_rect()

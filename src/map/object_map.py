"""
Atomic Bay'ttle
Paul Mairesse, Axel Loones, Louis Le Meilleur, Joseph Bénard, Théo de Aranjo
This file contain the definition of the pickable object in the game
"""
import pygame
import src.tools.constant as tools
from src.tools.tools import Vector2, MixeurAudio


_IMAGE_CACHE = {}


def load_object_image(path):
    key = str(path)
    if key not in _IMAGE_CACHE:
        image = pygame.image.load(path).convert_alpha()
        image.set_colorkey(image.get_at((0, 0)))
        _IMAGE_CACHE[key] = image
    return _IMAGE_CACHE[key]


class Object_map(pygame.sprite.Sprite):

    def __init__(self, name, pos, path):

        super().__init__()
        self.name = name
        self.image = load_object_image(path)
        self.rect = self.image.get_rect(topleft=pos)

    def handle(self, event, *args, **kargs):
        match event.type:
            case tools.INTERACT:
                if self.rect.colliderect(event.rect):
                    event.player.life_multiplicator = 0
                    self.kill()
            case tools.IMPACT:
                _dist = Vector2(self.rect.centerx - event.x, self.rect.centery - event.y)
                if _dist.lenght < event.radius * 2:
                    self.kill()
                    MixeurAudio.play_effect(tools.PATH / "assets" / "sound" / "explosion.wav")

    def update(self):
        ...

import pygame
from src.game import Camera

# rewrite of get_pos to send now the pos in the virtual surface and not the screen.


def get_pos(func):
    def wrap(abs=False):
        if abs:
            return func()
        else:
            coord = func()
            return Camera.to_virtual(*coord)
    return wrap


pygame.mouse.get_pos = get_pos(pygame.mouse.get_pos)


def mydraw(self, surface):
    sprites = self.sprites()
    if hasattr(surface, "blits"):
        self.spritedict.update(
            zip(sprites, surface.blits((spr.image, spr.rect) for spr in sprites if spr.visible)))
    else:
        for spr in sprites:
            if spr.visible:
                self.spritedict[spr] = surface.blit(spr.image, spr.rect)
    self.lostsprites = []
    dirty = self.lostsprites

    return dirty


pygame.sprite.Group.draw = mydraw
pygame.sprite.Sprite.visible = True

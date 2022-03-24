import pygame
import src.tools.constant as tools

class Object_map(pygame.sprite.Sprite):
    
    def __init__(self, name, pos,path):

        super().__init__()
        self.name=name
        self.image = pygame.image.load(path).convert_alpha()
        transColor = self.image.get_at((0,0))
        self.image.set_colorkey(transColor)
        self.rect = self.image.get_rect(topleft=pos)

    def handle(self,event):
        match event.type:
            case tools.INTERACT:
                if self.rect.colliderect(event.rect):
                    print("interraction")
            case tools.IMPACT:
                ...

    def update(self):
        ...
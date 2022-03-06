import pygame

CHARGING = pygame.USEREVENT + 1
ISPLAYING = pygame.USEREVENT + 2
ISLOCKED = pygame.USEREVENT + 3
ENDTURN = pygame.USEREVENT + 4
GRAVITY = pygame.USEREVENT + 4

TEAM = {
    "perso_1":{
        "idle":(24,28),
        "run":(25,30),
        "jump":(25,30),
        "fall":(25,28),
        "ground":(26,28),
        "speed_factor":1
    },
    "perso_2":{
        "idle":(42,29),
        "run":(40,29),
        "jump":(40,29),
        "fall":(40,29),
        "ground":(40,29),
        "speed_factor":0.75
    }
}
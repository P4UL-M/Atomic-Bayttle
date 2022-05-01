import pygame
import pathlib

PATH = pathlib.Path(__file__).parent.parent.parent

CHARGING = pygame.USEREVENT + 1
DEATH = pygame.USEREVENT + 2
IMPACT = pygame.USEREVENT + 3
ENDTURN = pygame.USEREVENT + 4
GRAVITY = pygame.USEREVENT + 5
INTERACT = pygame.USEREVENT + 6
ENDMUSIC = pygame.USEREVENT + 7

TEAM = {
    "perso_1": {
        "idle": (24, 28),
        "run": (25, 30),
        "jump": (26, 30),
        "fall": (25, 28),
        "ground": (26, 28),
        "emote": (64, 40),
        "losed": (64, 34, 2),
        "speed_factor": 1,
        "launcher_pivot": (1 / 2, 1 / 2),
        "melee_pivot": (1 / 5, 1 / 2),
        "auto_pivot": (1 / 2, 1 / 2),
    },
    "perso_2": {
        "idle": (42, 29),
        "run": (40, 29),
        "jump": (40, 29),
        "fall": (40, 29),
        "ground": (40, 29),
        "emote": (72, 29),
        "losed": (72, 32, 3),
        "speed_factor": 0.75,
        "launcher_pivot": (1 / 2, 1 / 2),
        "melee_pivot": (1 / 5, 1 / 2),
        "auto_pivot": (1 / 3, 1 / 2),
    },
    "perso_3": {
        "idle": (24, 28),
        "run": (25, 28),
        "fall": (24, 28),
        "jump": (27, 28),
        "ground": (26, 28),
        "emote": (31, 28),
        "losed": (34, 30, 2),
        "speed_factor": 1.25,
        "launcher_pivot": (1 / 3, 1 / 2),
        "melee_pivot": (1 / 5, 1 / 2),
        "auto_pivot": (1 / 4, 1 / 2),
    },
    "perso_4": {
        "idle": (31, 28),
        "run": (27, 28),
        "fall": (27, 28),
        "jump": (29, 28),
        "ground": (29, 28),
        "emote": (29, 28),
        "losed": (34, 30, 1),
        "speed_factor": 0.9,
        "launcher_pivot": (1 / 2, 1 / 2),
        "melee_pivot": (1 / 5, 1 / 2),
        "auto_pivot": (1 / 5, 1 / 5),
    }
}


class EndPartie(Exception):
    ...


class EndAction(Exception):
    ...

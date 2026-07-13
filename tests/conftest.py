import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


def pytest_sessionstart(session):
    pygame.init()
    pygame.display.set_mode((64, 64))


def pytest_sessionfinish(session, exitstatus):
    pygame.quit()

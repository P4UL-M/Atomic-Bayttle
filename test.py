import pygame
from pygame.constants import *
import time

pygame.init()
pygame.display.set_mode((1,1))

a = pygame.Surface((10000,10000)).convert(8)
a.fill((255,255,255))

t1 = time.time()
pygame.image.tostring(a, 'RGB')
print(time.time() - t1)


t1 = time.time()
pygame.image.tostring(a, 'P')
print(time.time() - t1)

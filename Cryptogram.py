import pygame
import Pyscreen
import random

pygame.init()

running = True
clock = pygame.time.Clock()
screen = Pyscreen.screen
width_ratio = Pyscreen.width_ratio
height_ratio = Pyscreen.height_ratio
while running:
    Pyscreen.update_screen_loop()
    Pyscreen.draw_screen_loop(screen, width_ratio, height_ratio)
    for event in pygame.event.get():
        Pyscreen.event_screen_loop(event)
        if event.type == pygame.QUIT:
            running = False
    clock.tick(60)
pygame.quit()

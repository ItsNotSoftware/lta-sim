import pygame
from ui import UI 


ui = UI(1400, 1600)

running = True
while running:
    ui.event_handler()
    ui.draw()
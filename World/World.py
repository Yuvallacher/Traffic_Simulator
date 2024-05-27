import pygame

class World:
    PIXELS_PER_METER = 5
    FPS = 60
    SCREEN_WIDTH = 1280 
    SCREEN_HEIGHT = 720
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def __init__(self, maxSpeed : int, frequency : int, politeness : int):
        self.maxSpeed = maxSpeed
        self.frequency = frequency
        self.politeness = politeness
        
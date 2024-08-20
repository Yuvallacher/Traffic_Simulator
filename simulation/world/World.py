import pygame
from simulation.world.road import Road

class World:
    NUMBER_OF_CARS = 100

    PIXELS_PER_METER = 5
    FPS = 60

    LANE_SIZE = 20
    NUMBER_OF_LANES = 5

    MAX_SPEED = 50
    FREQUENCY = 10
    POLITENESS = 8
    AWARENESS = 1
    PIXELS_PER_METER = 5
    
    FPS = 60
    SCREEN_WIDTH = 1280 
    SCREEN_HEIGHT = 720
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    GREY = (153, 163, 164)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    def __init__(self, roads : list[Road]):
        self.roads = roads


    def get_vehicle_road(self, roadIndex : int) -> Road:
        return self.roads[roadIndex]

        
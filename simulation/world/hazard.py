from pygame.surface import Surface
from pygame.math import Vector2

class Hazard:
    def __init__(self, type : str, location : Vector2, roadIndex : int, directionIndex : int, images : list[Surface], attributes : dict):
        self.type = type
        self.location = location
        self.roadIndex = roadIndex
        self.directionIndex = directionIndex
        self.images = images
        self.attributes = attributes
        
    
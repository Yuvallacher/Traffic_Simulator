import pygame
from simulation.data.Accident import AccidentManager
from simulation.world.road import RoadBuilder
from simulation.world.road import Road
from simulation.world.hazard import Hazard

class World:
    NUMBER_OF_CARS = 100

    PIXELS_PER_METER = 5
    FPS = 60

    LANE_SIZE = 20
    NUMBER_OF_LANES = 5

    MAX_SPEED = 50
    FREQUENCY = 10
    POLITENESS = 6
    AWARENESS = 1
    PIXELS_PER_METER = 5
    
    FPS = 60
    SCREEN_WIDTH = 1280 
    SCREEN_HEIGHT = 720
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    GREY = (153, 163, 164)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (119, 189, 40)
    
    def __init__(self, roadType : str, numberOfLanes : int):
        self.roads = RoadBuilder.create_road(roadType, numberOfLanes)
        self.vehiclesManager = None
        self.simulationRunning = True
        self.hazards : list[Hazard] = []
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.accidentManager =  AccidentManager()

    def set_vehicles_manager(self, vehiclesManager):
        self.vehiclesManager = vehiclesManager

    def get_vehicle_road(self, roadIndex : int) -> Road:
        return self.roads[roadIndex]

    def add_hazard(self, hazard : Hazard):
        self.hazards.append(hazard)
import pygame
from simulation.data.Accident import AccidentManager
from simulation.world.road import RoadBuilder
from simulation.world.road import Road
from simulation.world.hazard import TrafficLightsManager
from simulation.world.hazard import Hazard

class World:
    NUMBER_OF_CARS = 100
    SPAWN_RATE = 5

    PIXELS_PER_METER = 5
    FPS = 60

    LANE_SIZE = 20
    NUMBER_OF_LANES = 5

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
    
    def __init__(self, roadType : str, numberOfLanes : int, maxSpeed : float):
        self.roads = RoadBuilder.create_road(roadType, numberOfLanes)
        self.vehiclesManager = None
        self.simulationRunning = True
        self.simulationPaused = False
        self.maxSpeed = maxSpeed
        self.hazards : list[Hazard] = []
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.accidentManager = AccidentManager()
        self.trafficlightManager = TrafficLightsManager()

    def set_vehicles_manager(self, vehiclesManager):
        self.vehiclesManager = vehiclesManager

    def get_vehicle_road(self, roadIndex : int) -> Road:
        return self.roads[roadIndex]

    def add_hazard(self, hazard : Hazard):
        self.hazards.append(hazard)
        
    def search_closest_point_in_roads(self, coordinate : pygame.math.Vector2) -> dict:
        minimalDistance = float('inf')
        closestPoint = {}
        for roadIndex, road in enumerate(self.roads):
            for directionIndex, direction in enumerate(road.allLanesInRoad):
                for laneIndex, lane in enumerate(direction):
                    for coorIndex, pathCoordinate in enumerate(lane.path):
                        distanceToCoordinate = pathCoordinate.distance_to(coordinate)
                        if not road.is_point_part_of_junction(pathCoordinate) and not road.is_point_part_of_roundabout(pathCoordinate):
                            if distanceToCoordinate < minimalDistance and distanceToCoordinate <= 100:
                                minimalDistance = distanceToCoordinate
                                path = self.roads[roadIndex].allLanesInRoad[directionIndex][laneIndex].path
                                closestPoint["coordinate"] = pathCoordinate
                                closestPoint["nextCoordinate"] = path[coorIndex + 1]
                                closestPoint["roadIndex"] = roadIndex
                                closestPoint["directionIndex"] = directionIndex
                                closestPoint["laneIndex"] = laneIndex
                                closestPoint["nearJunction"] = False
                                closestPoint["junctionID"] = None
                                for i in range(1, 3):
                                    if len(path) > coorIndex + i:
                                        isNearJunction, _, junctionID = road.is_start_of_junction(path[coorIndex + i], directionIndex)
                                        if isNearJunction: 
                                            closestPoint["nearJunction"] = True
                                            closestPoint["junctionID"] = junctionID
                                            break
        return closestPoint
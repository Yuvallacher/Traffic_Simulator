import pygame
from simulation.vehicle.Vehicle import Vehicle
from simulation.vehicle.Vehicle import Car
from simulation.world.Point import Point
from simulation.world.road import Road
from simulation.world.World import World
from simulation.manager.vehicles_manager import VehiclesManager
from simulation.data.DataManager import DataManager


SCREEN_WIDTH = 1280 
SCREEN_HEIGHT = 720

PIXELS_PER_METER = 5
FPS = 60

NUMBER_OF_CARS = 100

LANE_SIZE = 20
NUMBER_OF_LANES = 5

MAX_SPEED = 100
FREQUENCY = 10
POLITENESS = 1

#colors
GREY = (153, 163, 164)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

red_car_image = pygame.transform.scale(pygame.image.load('carPictures\\redCar.png'), (25, 15))
purple_car_image = pygame.transform.scale(pygame.image.load('carPictures\\purpleCar.png'), (25, 15))
yellow_car_image = pygame.transform.scale(pygame.image.load('carPictures\\yellowCar.png'), (25, 15))
blue_car_image = pygame.transform.scale(pygame.image.load('carPictures\\blueCar.svg'), (25, 15))
black_car_image = pygame.transform.scale(pygame.image.load('carPictures\\blackCar.jpg'), (25, 15))
carPictures = [red_car_image, purple_car_image, yellow_car_image, blue_car_image, black_car_image]

red_truck_image = pygame.transform.scale(pygame.image.load('carPictures\\redTruck.png'), (60, 17))

def drawRoad(road : Road, screen):
    roadRect = pygame.Rect(0, 300, SCREEN_WIDTH, LANE_SIZE * NUMBER_OF_LANES)
    pygame.draw.rect(screen, GREY, roadRect)
    
    if road.numer_of_lanes >= 2:
        for i in range(road.numer_of_lanes - 1):
            coordinates = Point(road.starting_position.x, (road.lanes[i].y + road.lanes[i+1].y) / 2)
            while coordinates.x <= SCREEN_WIDTH:
                pygame.draw.line(screen, WHITE, (coordinates.x, coordinates.y), (coordinates.x + 5, coordinates.y), width=2)
                coordinates.x += 10


def updateCarPos(vehicles: list[Vehicle], simulationWorld : World, dataManager : DataManager):
    for vehicle in vehicles:
        vehicle.accelerateAndBreak(vehicles, simulationWorld, dataManager)
        vehicle.location.x += vehicle.speed
        

def drawCars(vehicles: list[Vehicle], screen):
    for vehicle in vehicles:
        if isinstance(vehicle, Car):
            screen.blit(carPictures[vehicle.colorIndex], (vehicle.location.x, vehicle.location.y - 7))
            #carPictures[vehicle.colorIndex].get_rect(topleft=(vehicle.location.x, vehicle.location.y - 7))     transform blit to rect so we can work woth points
        else:
            screen.blit(red_truck_image, (vehicle.location.x, vehicle.location.y - 8))
            #red_truck_image.get_rect(topleft=(vehicle.location.x, vehicle.location.y - 8))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


vehiclesManager = VehiclesManager(NUMBER_OF_CARS)

#roads 
road = Road(Point(0, 300), Point(SCREEN_WIDTH, 300), NUMBER_OF_LANES, LANE_SIZE)

#world creation
simulationWorld = World(maxSpeed=MAX_SPEED, frequency=FREQUENCY, politeness=POLITENESS, road=road)
simulationRunning = True

#clock
clock = pygame.time.Clock()

#dataManager
dataManager = DataManager(filename='simulation_data.xlsx', export_interval=2)
next_stat_update = pygame.time.get_ticks() + dataManager.export_interval * 1000  # Convert seconds to milliseconds


while simulationRunning:
    screen.fill(WHITE)
    drawRoad(road, screen)
    
    vehiclesManager.addCar(road.lanes, simulationWorld)
    updateCarPos(vehiclesManager.vehicles, simulationWorld, dataManager)
    drawCars(vehiclesManager.vehicles, screen)
    vehiclesManager.removeCars(SCREEN_WIDTH)
    
    current_time = pygame.time.get_ticks()
    if current_time >= next_stat_update:
        dataManager.update_stats(vehiclesManager.vehicles)
        next_stat_update = current_time + dataManager.export_interval * 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simulationRunning = False

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
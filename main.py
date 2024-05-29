import pygame
from vehicle.Vehicle import Vehicle
from vehicle.Vehicle import Car
from vehicle.Vehicle import Truck
from world.Point import Point
import random
import time
from simulation.manager.road import Road
from world.World import World
from simulation.manager.vehicles_manager import VehiclesManager


SCREEN_WIDTH = 1280 
SCREEN_HEIGHT = 720

PIXELS_PER_METER = 5
FPS = 60

NUMBER_OF_CARS = 50

LANE_SIZE = 20
NUMBER_OF_LANES = 5

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


def updateCarPos(vehicles: list[Vehicle], simulationWorld : World):
    for vehicle in vehicles:
        vehicle.accelerateAndBreak(vehicles, simulationWorld)
        vehicle.location.x += vehicle.speed
        

def drawCars(vehicles: list[Vehicle], screen):
    for vehicle in vehicles:
        if isinstance(vehicle, Car):
            screen.blit(carPictures[vehicle.colorIndex], (vehicle.location.x, vehicle.location.y - 7))
        else:
            screen.blit(red_truck_image, (vehicle.location.x, vehicle.location.y - 8))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

vehiclesManager = VehiclesManager(NUMBER_OF_CARS)

#world creation
simulationWorld = World(maxSpeed=100, frequency=10, politeness=4)
simulationRunning = True


#roads 
road = Road(Point(0, 300), Point(SCREEN_WIDTH, 300), NUMBER_OF_LANES, LANE_SIZE)

#clock
clock = pygame.time.Clock()


while simulationRunning:
    screen.fill(WHITE)
    drawRoad(road, screen)
    
    vehiclesManager.addCar(road.lanes, simulationWorld)
    updateCarPos(vehiclesManager.vehicles, simulationWorld)
    drawCars(vehiclesManager.vehicles, screen)
    vehiclesManager.removeCars(SCREEN_WIDTH)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simulationRunning = False

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
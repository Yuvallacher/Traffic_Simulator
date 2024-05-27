import pygame
from vehicle.Vehicle import Vehicle
from world.Point import Point
import random
import time
from world.World import World


SCREEN_WIDTH = 1280 
SCREEN_HEIGHT = 720

PIXELS_PER_METER = 5
FPS = 60

#colors
GREY = (153, 163, 164)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

num_of_cars = 25

red_car_image = pygame.transform.scale(pygame.image.load('carPictures\\redCar.png'), (25, 15))
purple_car_image = pygame.transform.scale(pygame.image.load('carPictures\\purpleCar.png'), (25, 15))
yellow_car_image = pygame.transform.scale(pygame.image.load('carPictures\\yellowCar.png'), (25, 15))
blue_car_image = pygame.transform.scale(pygame.image.load('carPictures\\blueCar.svg'), (25, 15))
black_car_image = pygame.transform.scale(pygame.image.load('carPictures\\blackCar.jpg'), (25, 15))
carPictures = [red_car_image, purple_car_image, yellow_car_image, blue_car_image, black_car_image]


def drawRoad(coordinates, screen, road):
    pygame.draw.rect(screen, GREY, road)
    while coordinates.x <= SCREEN_WIDTH:
        pygame.draw.line(screen, WHITE, (coordinates.x, coordinates.y), (coordinates.x + 5, coordinates.y), width=2)
        coordinates.x += 10


def addCar(cars: list[Vehicle], lanes: list, simulationWorld: World):
    if random.uniform(0, 1) >= 1 / (simulationWorld.frequency * 10):
        if len(cars) < num_of_cars:
            newCar = Vehicle(Point(-simulationWorld.maxSpeed, lanes[random.randint(0, len(lanes) - 1)] - 2.5), speed=simulationWorld.maxSpeed)
            newCar.setDesiredSpeed(simulationWorld.maxSpeed)
            cars.append(newCar)
            

def removeCars(cars : list[Vehicle]):
    for car in cars:
        if car.location.x > SCREEN_WIDTH:
            cars.remove(car)


def updateCarPos(cars: list[Vehicle], simulationWorld : World):
    for car in cars:
        car.accelerateAndBreak(cars, simulationWorld)
        car.location.x += car.speed
        

def drawCars(cars: list[Vehicle], screen):
    for car in cars:
        #pygame.draw.rect(screen, BLACK, (car.location.x, car.location.y, car.width, car.height))
        screen.blit(carPictures[car.colorIndex], (car.location.x, car.location.y - 3))


cars = []


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


#world creation
simulationWorld = World(maxSpeed=100, frequency=10, politeness=8)

simulationRunning = True


#lanes
lanes = [310, 330]

#roads 
lane_size = 20
number_of_lanes = 2
allRoad = pygame.Rect(0, 300, SCREEN_WIDTH, lane_size * number_of_lanes)


carXPosition = 0
carYPosition = lanes[0] - 3


clock = pygame.time.Clock()

while simulationRunning:
    screen.fill(WHITE)
    drawRoad(Point(0, 320), screen, allRoad)

    addCar(cars, lanes, simulationWorld)
    updateCarPos(cars, simulationWorld)
    drawCars(cars, screen)
    removeCars(cars)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simulationRunning = False


    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
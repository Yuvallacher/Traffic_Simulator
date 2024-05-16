import pygame
import Vehicle.Vehicle as Vehicle
import random
import time
import Point
import World.World as World

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720

#world settings
world = World.World(0.5, 2, 2)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

simulationRunning = True

#colors
GREY = (153, 163, 164)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#lanes
lanes = [307.5, 324]

#frames
clock = pygame.time.Clock()
fps = 300


#cars
cars = []

#roads 
road = pygame.Rect(0, 300, SCREEN_WIDTH, 33)

def addCars(frequency, cars):
    for lane in lanes:
        if random.uniform(0, 1) >= 1 / frequency and len(cars) < 5: 
            cars.append(Vehicle.Vehicle(Point.Point(-10, lane), random.uniform(0.1, 2), 2, world))

def switchLanes(cars, lanes: list):
    for car in cars:
        print(car.goToUpperLane)
        if car.goToLowerLane:
            car.position.y = lanes[1]
        if car.goToUpperLane:
            car.position.y = lanes[0]


def drawRoad(coordinate, screen):
    
    while coordinate.x <= SCREEN_WIDTH:
        pygame.draw.line(screen, WHITE, (coordinate.x, coordinate.y), (coordinate.x + 5, coordinate.y), width=2)
        coordinate.x += 10


while simulationRunning:
    clock.tick(fps)

    screen.fill(WHITE)
    pygame.draw.rect(screen, GREY, road)
    drawRoad(Point.Point(0, 315), screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simulationRunning = False
    closestCar = 800
    switchLanes(cars, lanes)
    for movingCar in cars:
        carCoordinate = Point.Point(float(movingCar.position.x,), float(movingCar.position.y,))
        movingCar.accelerateAndBreak(cars, world)
        movingCar.moveLaneRight(cars, world, Point.Point(0, lanes[1]))
        movingCar.moveLaneLeft(cars, world, Point.Point(0, lanes[0]))
        movingCar.position.x += movingCar.speed
        pygame.draw.circle(screen, BLACK, (carCoordinate.x, carCoordinate.y), 7.5)
        closestCar = min(closestCar, movingCar.position.x)
        if movingCar.position.x >= SCREEN_WIDTH:
            cars.remove(movingCar)
    if closestCar > 20:
        addCars(world.frequency, cars)
    pygame.display.update()

pygame.QUIT()


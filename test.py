import pygame
import vehicle.Vehicle as Vehicle
import random
import time
import world.World as World
from world.Point import Point

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720


world = World.World(maxSpeed=50, frequency=1, politeness=3.5)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

simulationRunning = True

#colors
GREY = (153, 163, 164)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#lanes
lanes = [307.5, 324]

#cars

carXPosition = -10
carYPosition = lanes[0]
cars = []

#roads 
road = pygame.Rect(0, 300, SCREEN_WIDTH, 33)

def addCars(frequency, cars):
    for lane in lanes:
        if random.uniform(0, 1) >= 1 / (frequency * 10): 
            newCar = Vehicle.Vehicle(Point(-10, lane))
            newCar.setDesiredSpeed(world.maxSpeed)
            cars.append(newCar)
            



def drawRoad(xPos, yPos, screen):
    
    while xPos <= SCREEN_WIDTH:
        pygame.draw.line(screen, WHITE, (xPos, yPos), (xPos + 5, yPos), width=2)
        xPos += 10



while simulationRunning:
    screen.fill(WHITE)
    pygame.draw.rect(screen, GREY, road)
    drawRoad(0, 315, screen)
    pygame.draw.circle(screen, BLACK, (carXPosition, carYPosition), 7.5)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simulationRunning = False
    closestCar = 800
    for movingCar in cars:
        carXPosition = float(movingCar.location.x)
        carYPosition = float(movingCar.location.y)
        movingCar.accelerateAndBreak(cars, world)
        movingCar.location.x += movingCar.speed
        pygame.draw.circle(screen, BLACK, (carXPosition, carYPosition), 7.5)
        closestCar = min(closestCar, movingCar.location.x)
        if movingCar.location.x >= SCREEN_WIDTH:
            cars.remove(movingCar)
    if closestCar > 20:
        addCars(world.frequency, cars)
    pygame.display.update()

pygame.QUIT()
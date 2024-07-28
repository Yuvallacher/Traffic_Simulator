import pygame
from calculations.straight_road import straightRoad
from simulation.vehicle.Vehicle import Vehicle
from simulation.world.Point import Point
import random
import time
from simulation.world.World import World

SCREEN_WIDTH = 1280 
SCREEN_HEIGHT = 720


PIXELS_PER_METER = 5
FPS = 60
car_speed_kmh = 60
car_speed_mps = car_speed_kmh * 1000 / 3600
car_speed_ppf = car_speed_mps * PIXELS_PER_METER / FPS

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

simulationRunning = True

#colors
GREY = (153, 163, 164)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#lanes
lanes = [307.5, 324]

#roads 
#road = pygame.Rect(0, 300, SCREEN_WIDTH, 33)
road = pygame.image.load('straightRoadPictures\\straightRoad.png')
road = pygame.transform.scale(road, (1280,150))
testRoad = straightRoad(2, (1280, 150))
testRoad.setRoadFunctionAsY(10)

carXPosition = 0
#carYPosition = lanes[0]- 3
carYPosition = lanes[0] - 3

car_image = pygame.image.load('carPictures\\redCar.png')
car_image = pygame.transform.scale(car_image,(25,15))
car_rect = car_image.get_rect()

car_rect.topleft = (0, lanes[0] - 3)
clock = pygame.time.Clock()

def drawRoad(coordinates, screen):
    
    while coordinates.x <= SCREEN_WIDTH:
        pygame.draw.line(screen, WHITE, (coordinates.x, coordinates.y), (coordinates.x + 5, coordinates.y), width=2)
        coordinates.x += 10

while simulationRunning:
    screen.fill(WHITE)
    screen.blit(testRoad.road, (0,200))
    #pygame.draw.rect(screen, GREY, road)
    #drawRoad(Point(0, 315), screen)
    carXPosition = (testRoad.getPoint(car_speed_ppf + carXPosition)).x
    car_rect.x = (testRoad.getPoint(car_speed_ppf + carXPosition)).x
    
    screen.blit(car_image, car_rect)
    pygame.draw.rect(screen, BLACK, (carXPosition, carYPosition,15, 10))
    print(f"Car rect x: {car_rect.x}, Rectangle x: {carXPosition}")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simulationRunning = False
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
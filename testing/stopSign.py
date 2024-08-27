import pygame
import random
import time

from pygame import Vector2


def convert_speed_to_pixels_per_frames(speed : float):
    car_speed_mps = speed * 1000 / 3600
    car_speed_ppf = car_speed_mps * PIXELS_PER_METER / FPS
    return car_speed_ppf

# def calculate_deceleration(distance, speed):
#     deceleration = -(speed ** 2) / (2 * distance)
#     return deceleration

def calculate_deceleration(distance, speed):
    if distance == 0:
        return float('inf')  # Prevent division by zero
    deceleration = (speed ** 2) / (2 * distance)
    return deceleration

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




stopSignImage = pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\stop.jpg").convert(), (30,70))
stopSignImageRect = stopSignImage.get_rect()
stopSignImageRect.topleft = Vector2(600,300)

car_image = pygame.image.load('pictures\\carPictures\\redCar.png')
car_image = pygame.transform.scale(car_image,(25,15))
car_rect = car_image.get_rect()
car_pos = Vector2(0,300)


car_rect.center = car_pos
clock = pygame.time.Clock()

speed = convert_speed_to_pixels_per_frames(120)
 

while simulationRunning:
    screen.fill(WHITE)
    screen.blit(stopSignImage, stopSignImageRect.topleft)
    screen.blit(car_image, car_rect)
    pygame.draw.rect(screen, (0, 255, 0), stopSignImageRect, 2)
    pygame.draw.line(screen,BLACK, stopSignImageRect.topleft, Vector2(600,280), 2)
    if car_pos.distance_to(stopSignImageRect.topleft) < 200:
        # speed -= 21.5532/ FPS**2
        distance = car_pos.distance_to(stopSignImageRect.topleft)
        deceleraiton = calculate_deceleration(distance, speed)
        speed -= deceleraiton 


    car_pos += Vector2(speed,0)
    car_rect.center = car_pos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simulationRunning = False

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
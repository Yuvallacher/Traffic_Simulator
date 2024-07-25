import pygame
from simulation.vehicle.Vehicle import Car
from simulation.vehicle.Vehicle import Vehicle
from pygame import Surface
import random

class VehicleDrawer:

    red_car_image = pygame.transform.scale(pygame.image.load('carPictures\\redCar.png'), (25, 15))
    purple_car_image = pygame.transform.scale(pygame.image.load('carPictures\\purpleCar.png'), (25, 15))
    yellow_car_image = pygame.transform.scale(pygame.image.load('carPictures\\yellowCar.png'), (25, 15))
    blue_car_image = pygame.transform.scale(pygame.image.load('carPictures\\blueCar.svg'), (25, 15))
    black_car_image = pygame.transform.scale(pygame.image.load('carPictures\\blackCar.jpg'), (25, 15))
    carPictures = [red_car_image, purple_car_image, yellow_car_image, blue_car_image, black_car_image]

    red_truck_image = pygame.transform.scale(pygame.image.load('carPictures\\redTruck.png'), (60, 17))

    @staticmethod
    def get_car_image() -> Surface:
        index = random.randint(0,4)
        return  VehicleDrawer.carPictures[index]
    
    @staticmethod
    def get_truck_image() -> Surface:
        return VehicleDrawer.red_truck_image

    # staticmethod
    # def draw_vehicles(self, vehicles: list[Vehicle], screen):
    #     for vehicle in vehicles:
    #         if isinstance(vehicle, Car):
    #             screen.blit(self.carPictures[vehicle.colorIndex], (vehicle.location.x, vehicle.location.y - 7))
    #         else:
    #             screen.blit(self.red_truck_image, (vehicle.location.x, vehicle.location.y - 8))


    @staticmethod
    def draw_vehicles(vehicles : list[Vehicle], screen):
        for vehicle in vehicles:
            screen.blit(vehicle.image, vehicle.rect.topleft)
            
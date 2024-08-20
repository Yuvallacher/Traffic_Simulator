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



    @staticmethod
    def draw_vehicles(vehicles : list[Vehicle], screen):
        for vehicle in vehicles:
            screen.blit(vehicle.rotatedImage, vehicle.rect.topleft)
                
            # pygame.draw.rect(screen, (0, 255, 0), vehicle.rect, 2)
            # VehicleDrawer.draw_hitbox(screen, vehicle)

    # @staticmethod
    # def draw_hitbox(screen , vehicle : 'Vehicle'):
    #     # Create a surface with the same dimensions as the mask
    #     hitbox_surface = pygame.Surface(vehicle.mask.get_size(), pygame.SRCALPHA)
        
    #     # Fill the surface with a semi-transparent color where the mask is set
    #     # hitbox_surface.fill((0, 255, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)

    #     # Fill the hitbox surface with a semi-transparent color
    #     for x in range(vehicle.mask.get_size()[0]):
    #         for y in range(vehicle.mask.get_size()[1]):
    #             if vehicle.mask.get_at((x, y)):
    #                 hitbox_surface.set_at((x, y), (0, 255, 0, 100))  # Green with 100 alpha
        
    #     # Draw the surface at the position of the rect
    #     screen.blit(hitbox_surface, vehicle.rect.topleft)        
            
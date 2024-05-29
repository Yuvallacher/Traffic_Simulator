from calculations.pixels_calculations import PixelsConverter
from world.Point import Point
from world.World import World
import random
from numpy.random import normal

class Vehicle:
    def __init__(self, location : Point, speed=60):
        self.location = location
        self.speed = PixelsConverter.convert_speed_to_pixels_per_frames(speed)
        self.desiredSpeed = 0.0
    
    
    def setDesiredSpeed(self, maxSpeed : int):
        self.desiredSpeed = PixelsConverter.convert_speed_to_pixels_per_frames(self.coefficient * maxSpeed)
    
    
    def checkDistance(self, other_vehicles : list['Vehicle'], world: World):
        front_of_vehicle = self.location.x + self.width
        vehicle_lane = self.location.y
        minimal_distance = 10 + world.politeness * 10

        for other_vehicle in other_vehicles:
            other_vehicle_lane = other_vehicle.location.y
            if abs(vehicle_lane - other_vehicle_lane) <= 5: #TODO: add checkLane method to Road class? it tells my lane based on my position
                back_of_other_vehicle = other_vehicle.location.x - 3
                front_of_other_vehicle = other_vehicle.location.x + other_vehicle.width
                if front_of_vehicle < back_of_other_vehicle or front_of_vehicle < front_of_other_vehicle:
                    distance = back_of_other_vehicle - front_of_vehicle
                    if distance < minimal_distance:
                        return False

        return True
    
    
    def checkSurroundings(self, other_vehicles : list['Vehicle'], world: World):
        front_of_vehicle = self.location.x + self.width
        vehicle_lane = self.location.y
        minimal_distance = 10 + world.politeness * 10
        #TODO: return here after finishing Road and Lane classes
        
        
    
    
    def accelerateAndBreak(self, other_vehicles : list['Vehicle'], world: World):
        max_acceleration = 2  
        max_deceleration = -5 

        #weight_factor = 1.5 if self.weight > 5 else 1.0

        acceleration_factor = max_acceleration / self.weight
        deceleration_factor = max_deceleration / self.weight

        cruising_speed_factor = 0.5 #TODO: shouldn't be a literal but related to the next vehicle's speed
        cruising_speed = self.desiredSpeed * cruising_speed_factor

        clear_space_ahead = self.checkDistance(other_vehicles, world)
        if clear_space_ahead:
            acceleration_speed = PixelsConverter.convert_speed_to_pixels_per_frames(acceleration_factor)
            if self.speed + acceleration_speed <= self.desiredSpeed:
                self.speed += acceleration_speed
            else:
                self.speed = self.desiredSpeed
        else:
            if self.speed > cruising_speed:
                deceleration_speed = PixelsConverter.convert_speed_to_pixels_per_frames(deceleration_factor)
                if self.speed + deceleration_speed > cruising_speed:
                    self.speed += deceleration_speed
                else:
                    self.speed = cruising_speed
            else:
                self.speed = cruising_speed





#---------------------Car---------------------#

class Car(Vehicle):
    def __init__(self, location : Point, speed=60):
        self.weight = 2
        self.width = 30
        self.height = 20
        self.coefficient = normal(1, 0.12)
        self.colorIndex = random.randint(0, 4)
        super().__init__(location, speed)
    
    
    
    
    
    
#--------------------Truck--------------------#
class Truck(Vehicle):
    def __init__(self, location : Point, speed=60):
        self.weight = 15
        self.width = 65
        self.height = 20
        self.coefficient = normal(0.8, 0.09)
        super().__init__(location, speed)
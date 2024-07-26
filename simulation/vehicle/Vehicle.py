from calculations.pixels_calculations import PixelsConverter
from simulation.data.DataManager import DataManager
#from simulation.world.Point import Point
from simulation.world.World import World
from simulation.world.World import Road
import random
from numpy.random import normal
from pygame.math import Vector2
from pygame import transform
from pygame import Surface
import math

CAR_AVG_SPEED = 1
CAR_STANDARD_DEVIATION = 0.12
TRUCK_AVG_SPEED = 0.8
TRUCK_STANDARD_DEVIATION = 0.09

class Vehicle:
    def __init__(self, location : Vector2, directionIndex : int, laneIndex : int, driveAngle : float, image : Surface ,speed=60):
        self.location = location
        self.speed = PixelsConverter.convert_speed_to_pixels_per_frames(speed)
        self.desiredSpeed = 0.0
        self.directionIndex = directionIndex
        self.laneIndex = laneIndex
        self.targetPositionIndex = 0
        self.inAccident = False
        self.driveAngle = driveAngle
        self.image = image
        self.rect = image.get_rect()

        

    def update_vehicle_location(self, targetPos : Vector2, speed):
        direction = targetPos - self.location
        self.driveAngle = -math.degrees(math.atan2(direction.y,direction.x))
        self.rotate_vehicle()
        distance = direction.length() # TODO add case for speed == 0?
        if distance > speed:
            direction.scale_to_length(speed)
            self.location += direction

        else:
            self.location.update(targetPos)
            self.targetPositionIndex += 1 #TODO check what happens when a vehicle gets to the end of the lane. theoretically speaking, the vehicle should get removed

    def rotate_vehicle(self):
        self.image = transform.rotate(self.image, self.driveAngle)
        self.rect = self.image.get_rect(center=self.location)
         
    
    def setDesiredSpeed(self, maxSpeed : int):
        self.desiredSpeed = PixelsConverter.convert_speed_to_pixels_per_frames(self.coefficient * maxSpeed)
    
    
    def checkDistance(self, other_vehicles : list['Vehicle'], world: World, dataManager : DataManager):
        back_of_vehicle = self.location.x
        front_of_vehicle = self.location.x + self.length
        minimal_distance = 10 + world.POLITENESS * 10

        for other_vehicle in other_vehicles:
            if self != other_vehicle:
                if self.laneIndex == other_vehicle.laneIndex:
                    back_of_other_vehicle = other_vehicle.location.x - 3
                    front_of_other_vehicle = other_vehicle.location.x + other_vehicle.length
                    # start of accidents detection
                    if front_of_vehicle >= back_of_other_vehicle + 3 and back_of_vehicle <= front_of_other_vehicle:
                        if not (self.inAccident and other_vehicle.inAccident):
                            dataManager.log_accident(type(self).__name__, type(other_vehicle).__name__, PixelsConverter.convert_pixels_per_frames_to_speed(self.speed), PixelsConverter.convert_pixels_per_frames_to_speed(other_vehicle.speed))
                        self.inAccident = True
                        self.speed = 0
                        other_vehicle.inAccident = True
                        other_vehicle.speed = 0
                        return False
                    # end of accident detection
                    if front_of_vehicle < back_of_other_vehicle or front_of_vehicle < front_of_other_vehicle:
                        distance = back_of_other_vehicle - front_of_vehicle
                        if distance < minimal_distance:
                            return False

        return True
    
    
    def get_all_harazds_around_vehicle(self, other_vehicles : list['Vehicle'], road : Road, politeness : int) -> dict:
        """
        The vehicle scans its sorroundings for hazards, oncoming traffic, and other variables that can influence the driver's decision
        """
        surroundings = {}
        surroundings['vehicles'] = []
        #TODO: more checks for surroundings like hazards, turns, etc.
        
        front_of_vehicle = self.location.x + self.length
        minimal_distance = 10 + politeness * 10
        
        for other_vehicle in other_vehicles:
            if self != other_vehicle:
                if self.lane == other_vehicle.lane:
                    back_of_other_vehicle = other_vehicle.location.x - 3
                    front_of_other_vehicle = other_vehicle.location.x + other_vehicle.length
                    if front_of_vehicle < back_of_other_vehicle or front_of_vehicle < front_of_other_vehicle:
                        distance = back_of_other_vehicle - front_of_vehicle
                        if distance < minimal_distance:
                            surroundings['vehicles'].append(other_vehicle)

        
        return surroundings
        

    def makeNextDesicion(self, obstacles: list):
        #TODO implement lane swap
        #TODO implement decision
        pass 
    
    
    def accelerateAndBreak(self, other_vehicles : list['Vehicle'], world: World, dataManager : DataManager, road : Road):
        """
        Caculates and updates a vehicle's speed according to the road's conditions - traffic lights, hazards, etc.
        Then updates the vehicle's position based on its new speed
        """
        max_acceleration = 2  
        max_deceleration = -5 

        acceleration_factor = max_acceleration / self.weight
        deceleration_factor = max_deceleration / self.weight

        cruising_speed_factor = 0.5 #TODO: shouldn't be a literal but related to the next vehicle's speed
        cruising_speed = self.desiredSpeed * cruising_speed_factor

        #clear_space_ahead = self.checkDistance(other_vehicles, world, dataManager)
        #if clear_space_ahead:
        if True: #TODO DONT FORGET TO REMOVE THIS SHIT!!
            acceleration_speed = PixelsConverter.convert_speed_to_pixels_per_frames(acceleration_factor)
            if self.speed + acceleration_speed <= self.desiredSpeed:
                self.speed += acceleration_speed
            else:
                self.speed = self.desiredSpeed
        else:
            if self.inAccident == True:
                self.speed = 0
            else:
                if self.speed > cruising_speed:
                    deceleration_speed = PixelsConverter.convert_speed_to_pixels_per_frames(deceleration_factor)
                    if self.speed + deceleration_speed > cruising_speed:
                        self.speed += deceleration_speed
                    else:
                        self.speed = cruising_speed
                else:
                    self.speed = cruising_speed
        
        nextTargetPosition = road.get_next_target_position(self.directionIndex, self.laneIndex, self.targetPositionIndex)
        self.update_vehicle_location(nextTargetPosition, self.speed) # TODO add target position somehow
        




#---------------------Car---------------------#
class Car(Vehicle):
    def __init__(self, location : Vector2, directionIndex : int, laneIndex : int, driveAngle : float, image : Surface, speed=60):
        self.weight = 2
        self.length = 30
        self.width = 20
        self.coefficient = normal(CAR_AVG_SPEED, CAR_STANDARD_DEVIATION)
        self.colorIndex = random.randint(0, 4)
        super().__init__(location, directionIndex, laneIndex, driveAngle, image, speed)
    
    
    
    
    
    
#--------------------Truck--------------------#
class Truck(Vehicle):
    def __init__(self, location : Vector2, directionIndex : int, laneIndex : int, driveAngle : float, image : Surface, speed=60):
        self.weight = 15
        self.length = 65
        self.width = 20
        self.coefficient = normal(TRUCK_AVG_SPEED, TRUCK_STANDARD_DEVIATION)
        super().__init__(location, directionIndex, laneIndex, driveAngle, image, speed)
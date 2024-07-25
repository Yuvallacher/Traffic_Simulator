from calculations.pixels_calculations import PixelsConverter
from simulation.data.DataManager import DataManager
#from simulation.world.Point import Point
from simulation.world.World import World
from simulation.world.World import Road
import random
from numpy.random import normal
from pygame.math import Vector2

CAR_AVG_SPEED = 1
CAR_STANDARD_DEVIATION = 0.12
TRUCK_AVG_SPEED = 0.8
TRUCK_STANDARD_DEVIATION = 0.09

class Vehicle:
    def __init__(self, location : Vector2, lane : int, speed=60):
        self.location = location
        self.speed = PixelsConverter.convert_speed_to_pixels_per_frames(speed)
        self.desiredSpeed = 0.0
        self.lane = lane        # the lane's index in lanes[] variable of the road
        self.targetPositionIndex = 0
        self.inAccident = False

    # Function to move the object towards the next point in the path
    def updateVehicleLocation(self, target_pos : Vector2, speed):
        direction = target_pos - self.location
        distance = direction.length() # TODO add case for speed == 0?
        if distance > speed:
            direction.scale_to_length(speed)
            self.location += direction
        else:
            self.location.update(target_pos)
     
    
    def setDesiredSpeed(self, maxSpeed : int):
        self.desiredSpeed = PixelsConverter.convert_speed_to_pixels_per_frames(self.coefficient * maxSpeed)
    
    
    def checkDistance(self, other_vehicles : list['Vehicle'], world: World, dataManager : DataManager):
        back_of_vehicle = self.location.x
        front_of_vehicle = self.location.x + self.length
        minimal_distance = 10 + world.politeness * 10

        for other_vehicle in other_vehicles:
            if self != other_vehicle:
                if self.lane == other_vehicle.lane:
                    back_of_other_vehicle = other_vehicle.location.x - 3
                    front_of_other_vehicle = other_vehicle.location.x + other_vehicle.length
                    if front_of_vehicle >= back_of_other_vehicle + 3 and back_of_vehicle <= front_of_other_vehicle:
                        #if self.inAccident != other_vehicle.inAccident or (not self.inAccident and not other_vehicle.inAccident):
                        if not (self.inAccident and other_vehicle.inAccident):
                            dataManager.log_accident(type(self).__name__, type(other_vehicle).__name__, PixelsConverter.convert_pixels_per_frames_to_speed(self.speed), PixelsConverter.convert_pixels_per_frames_to_speed(other_vehicle.speed))
                        self.inAccident = True
                        self.speed = 0
                        other_vehicle.inAccident = True
                        other_vehicle.speed = 0
                        return False
                    if front_of_vehicle < back_of_other_vehicle or front_of_vehicle < front_of_other_vehicle:
                        distance = back_of_other_vehicle - front_of_vehicle
                        if distance < minimal_distance:
                            return False

        return True
    
    
    def checkSurroundings(self, other_vehicles : list['Vehicle'], road : Road, politeness : int):
        surroundings = {}
        surroundings['vehicles'] = []
        #TODO: more checks for surroundings like hazards, turns, etc.
        
        front_of_vehicle = self.location.x + self.length
        minimal_distance = 10 + politeness * 10
        
        for other_vehicle in other_vehicles:
            if self.lane == other_vehicle.lane:
                back_of_other_vehicle = other_vehicle.location.x - 3
                front_of_other_vehicle = other_vehicle.location.x + other_vehicle.length
                if front_of_vehicle < back_of_other_vehicle or front_of_vehicle < front_of_other_vehicle:
                    distance = back_of_other_vehicle - front_of_vehicle
                    if distance < minimal_distance:
                        surroundings['vehicles'].append(other_vehicle)

        
        return surroundings
        
        
    
    
    def accelerateAndBreak(self, other_vehicles : list['Vehicle'], world: World, dataManager : DataManager):
        max_acceleration = 2  
        max_deceleration = -5 

        acceleration_factor = max_acceleration / self.weight
        deceleration_factor = max_deceleration / self.weight

        cruising_speed_factor = 0.5 #TODO: shouldn't be a literal but related to the next vehicle's speed
        cruising_speed = self.desiredSpeed * cruising_speed_factor

        clear_space_ahead = self.checkDistance(other_vehicles, world, dataManager)
        if clear_space_ahead:
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
            
        self.updateVehicleLocation(_, self.speed) # TODO add target position somehow
        




#---------------------Car---------------------#
class Car(Vehicle):
    def __init__(self, location : Vector2, lane : int, speed=60):
        self.weight = 2
        self.length = 30
        self.width = 20
        self.coefficient = normal(CAR_AVG_SPEED, CAR_STANDARD_DEVIATION)
        self.colorIndex = random.randint(0, 4)
        super().__init__(location, lane, speed)
    
    
    
    
    
    
#--------------------Truck--------------------#
class Truck(Vehicle):
    def __init__(self, location : Vector2, lane : int, speed=60):
        self.weight = 15
        self.length = 65
        self.width = 20
        self.coefficient = normal(TRUCK_AVG_SPEED, TRUCK_STANDARD_DEVIATION)
        super().__init__(location, lane, speed)
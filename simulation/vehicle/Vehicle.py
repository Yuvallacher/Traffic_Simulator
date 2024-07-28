from calculations.pixels_calculations import PixelsConverter
from simulation.data.DataManager import DataManager
from calculations.polygon_calculations import QuadCalculation
from simulation.world.World import World
from simulation.world.World import Road
from numpy.random import normal
from pygame.math import Vector2
from pygame import transform
from pygame import Surface
import random
import math

CAR_AVG_SPEED = 1
CAR_STANDARD_DEVIATION = 0.12
TRUCK_AVG_SPEED = 0.8
TRUCK_STANDARD_DEVIATION = 0.09

class Vehicle:
    def __init__(self, location : Vector2, speedCoefficient : float, directionIndex : int, currentLaneIndex : int, driveAngle : float, image : Surface ,speed=60):
        self.location = location
        self.speed = PixelsConverter.convert_speed_to_pixels_per_frames(speed)
        self.desiredSpeed = 0.0
        self.speedCoefficient = speedCoefficient
        self.directionIndex = directionIndex
        self.currentLaneIndex = currentLaneIndex
        self.desiredLaneIndex = self.currentLaneIndex
        self.targetPositionIndex = 0
        self.inAccident = False
        self.driveAngle = driveAngle
        self.originalImage = image
        self.rotatedImage = self.originalImage
        self.rect = image.get_rect()

        
    def drive(self, allVehicles : list['Vehicle'], world: World, dataManager : DataManager, road : Road):
        """
        scan the surroundings, compute the next decision and execute it
        """
        allHazards = self.get_all_harazds_around_vehicle(allVehicles, road, world.POLITENESS, dataManager)
        if not self.inAccident:
            self.make_next_desicion(road, world, allHazards, dataManager)
        
    
    def make_next_desicion(self, road : Road, world : World, allHazards : dict, dataManager : DataManager):
        """
        compute and execute the next decision based on the surroindings
        """
        self.upgradedAccelerateAndBreak(allHazards['vehicle_ahead'], dataManager) 
        
        #TODO implement lane swap
        #TODO implement decision
        pass 
    
    def update_vehicle_location(self, targetPos: Vector2, speed):
        direction = targetPos - self.location
        desiredAngle = (-math.degrees(math.atan2(direction.y, direction.x))) % 360
        
        #if (desiredAngle != self.driveAngle and desiredAngle != -self.driveAngle) or desiredAngle == 0:
        if desiredAngle != self.driveAngle:
            self.driveAngle = desiredAngle
            self.rotate_vehicle()

        distance = direction.length()
        if distance > speed:
            direction.scale_to_length(speed)
            self.location += direction
        else:
            self.location.update(targetPos)
            self.targetPositionIndex += 1

        self.rect.center = self.location
            
            
    def rotate_vehicle(self):
        self.rotatedImage = transform.rotate(self.originalImage, self.driveAngle)
        self.rect = self.rotatedImage.get_rect(center=self.location)
         
    
    def setDesiredSpeed(self, maxSpeed : int):
        self.desiredSpeed = PixelsConverter.convert_speed_to_pixels_per_frames(self.speedCoefficient * maxSpeed)
    
    
    def checkDistance(self, other_vehicles : list['Vehicle'], world: World, dataManager : DataManager):
        back_of_vehicle = self.location.x
        front_of_vehicle = self.location.x + self.length
        minimal_distance = 10 + world.POLITENESS * 10

        for other_vehicle in other_vehicles:
            if self != other_vehicle:
                if self.currentLaneIndex == other_vehicle.currentLaneIndex:
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
    
    
    def get_all_harazds_around_vehicle(self, allVehicles : list['Vehicle'], road : Road, politeness : int, dataManager : DataManager) -> dict:
        """
        The vehicle scans its sorroundings for hazards, oncoming traffic, and other variables that can influence the driver's decision
        """
        surroundings = {}
        surroundings['vehicles'] = []
        surroundings['vehicle_ahead'] = None

        targetPosition = road.get_target_position[self.directionIndex, self.currentLaneIndex, self.targetPositionIndex]
        direction = (targetPosition - self.location).normalize()

        #TODO: more checks for surroundings like hazards, turns, etc.
        # fieldOfView = QuadCalculation.create_quad(self.rotatedImage.get_rect())
                
        for other_vehicle in allVehicles:
            if self != other_vehicle:
                if self.rotatedImage.get_rect().colliderect(other_vehicle.rotatedImage.get_rect()):
                    if not (self.inAccident and other_vehicle.inAccident):
                        dataManager.log_accident(type(self).__name__, type(other_vehicle).__name__, PixelsConverter.convert_pixels_per_frames_to_speed(self.speed), PixelsConverter.convert_pixels_per_frames_to_speed(other_vehicle.speed))
                    self.inAccident = True
                    self.speed = 0
                    other_vehicle.inAccident = True
                    other_vehicle.speed = 0
                    return
                else:
                    frontFov = self.create_fov_boundary(direction, leftAngle=-30, rightAngle=30, fovDistance=200)
                    leftSideFov = self.create_fov_boundary(direction, leftAngle=-120, rightAngle=-30, fovDistance=45)                    
                    rightSideFov = self.create_fov_boundary(direction, leftAngle=30, rightAngle=120, fovDistance=45)                    
        
        #         elif QuadCalculation.point_in_quad(other_vehicle.location, fieldOfView):
        #             surroundings['vehicles'].append(other_vehicle)
                    
                
        # surroundings['vehicle_ahead'] = self.get_vehicle_ahead(surroundings['vehicles'], road)
        return surroundings
    
    def create_fov_boundary_222222(center : Vector2, corner1 : Vector2, corner2 : Vector2) -> tuple[Vector2, Vector2]:
        leftBoundary = (corner1 - center)
        rightBoundary = (corner2 - center)
        
        return (leftBoundary, rightBoundary)
    
    def is_object_in_fov_2222222(self, objectLocation : Vector2, leftBoundary : Vector2, rightBoundary : Vector2, vehicleBorder :Vector2, fovDistance : int):
        objectToVehicleVector = objectLocation - vehicleBorder
        cross_left = leftBoundary.cross(objectToVehicleVector)
        cross_right = rightBoundary.cross(objectToVehicleVector)
        return cross_left >= 0 and cross_right <= 0 and objectToVehicleVector.length() <= fovDistance
    

    def create_fov_boundary(direction : Vector2, leftAngle : float, rightAngle : float, fovDistance : int):
        left_boundary = direction.rotate(leftAngle) * fovDistance
        right_boundary = direction.rotate(rightAngle) * fovDistance
        return (left_boundary, right_boundary)


    def is_object_in_fov(self, objectLocation : Vector2, leftBoundary : Vector2, rightBoundary : Vector2, fovDistance : int):
        objectToVehicleVector = objectLocation - self.location
        cross_left = leftBoundary.cross(objectToVehicleVector)
        cross_right = rightBoundary.cross(objectToVehicleVector)
        return cross_left >= 0 and cross_right <= 0 and objectToVehicleVector.length() <= fovDistance


    # TODO remove from comment!!
    
    # def get_vehicle_ahead(self, allVehiclesInFieldOfView : list['Vehicle'], road : Road) -> 'Vehicle':
    #     direction = road[self.directionIndex][self.currentLaneIndex].path[self.targetPositionIndex] - self.location
    #     targetPositionVector = road[self.directionIndex][self.currentLaneIndex].path[self.targetPositionIndex]
    #     pathDirection = 
    #     if len(allVehiclesInFieldOfView) == 0:
    #         return None
    #     else:
    #         currentVehicleAhead = None
    #         minDistance = 0
    #         for vehicle in allVehiclesInFieldOfView:
    #             if (self.directionIndex == vehicle.directionIndex):
    #                 if ( self.currentLaneIndex == vehicle.currentLaneIndex or self.currentLaneIndex == vehicle.desiredLaneIndex):
    #                     distance = self.location.distance_to(vehicle.location)
    #                     vehicleProjection =     
  
    
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
        
        nextTargetPosition = road.get_target_position(self.directionIndex, self.currentLaneIndex, self.targetPositionIndex + 1)
        self.update_vehicle_location(nextTargetPosition, self.speed) # TODO add target position somehow
        



    def upgradedAccelerateAndBreak(self, vehicleAhead : 'Vehicle', dataManager : DataManager):
        """
        Caculates and updates a vehicle's speed according to the road's conditions - other vehicles, hazards, etc.
        """
        max_acceleration = 2  
        max_deceleration = -5 

        acceleration_factor = max_acceleration / self.weight
        deceleration_factor = max_deceleration / self.weight

        cruising_speed_factor = 0.5 #TODO: shouldn't be a literal but related to the next vehicle's speed
        cruising_speed = self.desiredSpeed * cruising_speed_factor

        clearSpaceAhead = (vehicleAhead == None)
        if clearSpaceAhead:
            acceleration_speed = PixelsConverter.convert_speed_to_pixels_per_frames(acceleration_factor)
            if self.speed + acceleration_speed <= self.desiredSpeed:
                self.speed += acceleration_speed
            else:
                self.speed = self.desiredSpeed
        else:
            x = 10 # just to remove error, DELETE LINE LATER
            # if self.inAccident == True:
            #     self.speed = 0
            # else:
            #     if self.speed > cruising_speed:
            #         deceleration_speed = PixelsConverter.convert_speed_to_pixels_per_frames(deceleration_factor)
            #         if self.speed + deceleration_speed > cruising_speed:
            #             self.speed += deceleration_speed
            #         else:
            #             self.speed = cruising_speed
            #     else:
            #         self.speed = cruising_speed

#---------------------Car---------------------#
class Car(Vehicle):
    def __init__(self, location : Vector2, directionIndex : int, laneIndex : int, driveAngle : float, image : Surface, speed=60):
        self.weight = 2
        self.length = 30
        self.width = 20
        self.colorIndex = random.randint(0, 4)
        speedCoefficient = normal(CAR_AVG_SPEED, CAR_STANDARD_DEVIATION)
        super().__init__(location, speedCoefficient, directionIndex, laneIndex, driveAngle, image, speed)
    
    
    
    
    
    
#--------------------Truck--------------------#
class Truck(Vehicle):
    def __init__(self, location : Vector2, directionIndex : int, laneIndex : int, driveAngle : float, image : Surface, speed=60):
        self.weight = 15
        self.length = 65
        self.width = 20
        speedCoefficient = normal(TRUCK_AVG_SPEED, TRUCK_STANDARD_DEVIATION)
        super().__init__(location, speedCoefficient, directionIndex, laneIndex, driveAngle, image, speed)
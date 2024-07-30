from calculations.pixels_calculations import PixelsConverter
from simulation.data.DataManager import DataManager
from calculations.polygon_calculations import QuadCalculation
from simulation.world.World import World
from simulation.world.World import Road
from numpy.random import normal
from pygame.math import Vector2
from pygame import transform
from pygame import Surface
from pygame.rect import Rect
import random
import math

CAR_AVG_SPEED = 1
CAR_STANDARD_DEVIATION = 0.12
TRUCK_AVG_SPEED = 0.8
TRUCK_STANDARD_DEVIATION = 0.09

class Vehicle:
    def __init__(self, location : Vector2, speedCoefficient : float, directionIndex : int, currentLaneIndex : int, driveAngle : float, image : Surface, weight : float, width : int, length : int, speed=60):
        self.location = location
        self.speed = PixelsConverter.convert_speed_to_pixels_per_frames(speed)
        self.desiredSpeed = 0.0
        self.weight = weight
        self.width = width
        self.length = length
        self.widthOffset = self.width / 2
        self.lengthOffset = self.length / 2
        self.speedCoefficient = speedCoefficient
        self.directionIndex = directionIndex
        self.currentLaneIndex = currentLaneIndex
        self.desiredLaneIndex = self.currentLaneIndex
        self.targetPositionIndex = 0
        self.inAccident = False
        self.shouldSwitchLane = False
        self.activelySwitchingLane = False
        self.driveAngle = driveAngle
        self.originalImage = image
        self.rotatedImage = self.originalImage
        self.rect = image.get_rect()

        
    def drive(self, allVehicles : list['Vehicle'], world: World, dataManager : DataManager, road : Road):
        """
        scan the surroundings, compute the next decision and execute it
        """
        allHazards = self.get_all_harazds_around_vehicle(allVehicles, road, dataManager)
        if not self.inAccident:
            self.make_next_desicion(road, world, allHazards, dataManager)
        
    
    def make_next_desicion(self, road : Road, world : World, allHazards : dict, dataManager : DataManager):
        """
        compute and execute the next decision based on the surroindings
        """
        self.accelerateAndBreak(allHazards['vehicle_ahead'], world.POLITENESS)
        
        self.shouldSwitchLane = self.switching_lane_decision(allHazards['vehicle_ahead'])
        if self.shouldSwitchLane or self.activelySwitchingLane:
            self.switch_lane(allHazards['vehicle_ahead'], allHazards['vehicles_left'], allHazards['vehicles_right'], road)
        
        nextTargetPosition = road.get_target_position(self.directionIndex, self.desiredLaneIndex, self.targetPositionIndex + 1)
        self.update_vehicle_location(nextTargetPosition, self.speed) # TODO add target position somehow
        
        #TODO implement lane swap
        #TODO implement rest of decision
        pass 
    
    
    def switching_lane_decision(self, vehicleAhead : 'Vehicle') -> bool:
        """
        Determines whether a vehicle will try to switch a lane
        """
        shouldSwitchLane = False
        
        if vehicleAhead is not None:
            if vehicleAhead.speed < self.speed:
                speedDifference = PixelsConverter.convert_pixels_per_frames_to_speed(self.speed) - PixelsConverter.convert_pixels_per_frames_to_speed(vehicleAhead.speed)
                maxSpeedDifference = 25
                probabilityOfSwitching = min(1.0, speedDifference / maxSpeedDifference)
                shouldSwitchLane = random.random() < probabilityOfSwitching
        
        return shouldSwitchLane
    
    
    def switch_lane(self, vehicleAhead : 'Vehicle', vechidlesLeft : list['Vehicle'], vechilesRight : list['Vehicle'], road : Road):
        """
        Actively switch lanes. This method determines to which lane the vehicle should move and set a course to that lane
        """
        if self.activelySwitchingLane:
            return
        else: 
            pass 
            # TODO check neighboor lanes and decide which is the target. set desiredLaneIndex to that lane
            # if no lane is available, do NOT make activelySwitchingLane True. it should only become True when the actual lane switching has begun. 
            # in this scenario (no available lanes) desiredLaneIndex STAYS THE SAME and shouldSwitchLane STAYS TRUE
            
            
    
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
    
   
    
    def get_all_harazds_around_vehicle(self, allVehicles : list['Vehicle'], road : Road, dataManager : DataManager) -> dict:
        """
        The vehicle scans its sorroundings for hazards, oncoming traffic, and other variables that can influence the driver's decision
        """
        surroundings = {}
        surroundings['vehicles_front'] = []
        surroundings['vehicles_left'] = []
        surroundings['vehicles_right'] = []
        surroundings['vehicle_ahead'] = None
        
        targetPosition = road.get_target_position(self.directionIndex, self.currentLaneIndex, self.targetPositionIndex)
        if self.targetPositionIndex <= 3 or targetPosition == self.location :
            return surroundings
        direction = (self.location - targetPosition).normalize()

        #TODO: more checks for surroundings like hazards, turns, etc.
        
        for other_vehicle in allVehicles:
            if self != other_vehicle:
                if self.rect.colliderect(other_vehicle.rect):
                    if not (self.inAccident and other_vehicle.inAccident):
                        dataManager.log_accident(type(self).__name__, type(other_vehicle).__name__, PixelsConverter.convert_pixels_per_frames_to_speed(self.speed), PixelsConverter.convert_pixels_per_frames_to_speed(other_vehicle.speed))
                    self.inAccident = True
                    self.speed = 0
                    self.desiredSpeed = 0
                    other_vehicle.inAccident = True
                    other_vehicle.speed = 0
                    other_vehicle.desiredSpeed = 0
                    return surroundings
                else:
                    frontFov = self.create_fov_boundary(direction, -45, 45, 200)
                    leftSideFov = self.create_fov_boundary(direction, -170, -45, 200)                    
                    rightSideFov = self.create_fov_boundary(direction, 45, 170, 200)
                    if self.is_object_in_fov(other_vehicle.location, frontFov[0], frontFov[1], 200):
                        surroundings['vehicles_front'].append(other_vehicle)
                    elif self.is_object_in_fov(other_vehicle.location, leftSideFov[0], leftSideFov[1], 200):
                        surroundings['vehicles_left'].append(other_vehicle)
                    elif self.is_object_in_fov(other_vehicle.location, rightSideFov[0], rightSideFov[1], 200):
                        surroundings['vehicles_right'].append(other_vehicle)                    
                
        surroundings['vehicle_ahead'] = self.get_vehicle_ahead(surroundings['vehicles_front'], road)
        return surroundings
    

    #TODO move to calculations ?
    def create_fov_boundary(self, direction : Vector2, leftAngle : float, rightAngle : float, fovDistance : int):
        left_boundary = direction.rotate(leftAngle) * fovDistance
        right_boundary = direction.rotate(rightAngle) * fovDistance
        return (left_boundary, right_boundary)


    def is_object_in_fov(self, objectLocation : Vector2, leftBoundary : Vector2, rightBoundary : Vector2, fovDistance : int):
        objectToVehicleVector = objectLocation - self.location
        cross_left = leftBoundary.cross(objectToVehicleVector)
        cross_right = rightBoundary.cross(objectToVehicleVector)
        return cross_left >= 0 and cross_right <= 0 and objectToVehicleVector.length() <= fovDistance


    def get_vehicle_ahead(self, allVehiclesInFront : list['Vehicle'], road : Road) -> 'Vehicle':
        if len(allVehiclesInFront) == 0:
            return None
        else:
            currentVehicleAhead = None
            minDistance = 0
            first = True
            for vehicle in allVehiclesInFront:
                if self.directionIndex == vehicle.directionIndex:
                    if self.currentLaneIndex == vehicle.currentLaneIndex or self.currentLaneIndex == vehicle.desiredLaneIndex or self.desiredLaneIndex == vehicle.currentLaneIndex or self.desiredLaneIndex == vehicle.desiredLaneIndex:
                         distance = self.location.distance_to(vehicle.location)
                         if first == True:
                            minDistance = distance
                            currentVehicleAhead = vehicle
                            first = False
                         else:
                             if distance < minDistance:
                                minDistance = distance
                                currentVehicleAhead = vehicle
            return currentVehicleAhead                    
                                
    
    
    # def upgradedAccelerateAndBreak(self, vehicleAhead : 'Vehicle', politeness : int):
    #     """
    #     Caculates and updates a vehicle's speed according to the road's conditions - other vehicles, hazards, etc.
    #     """
    #     minimal_distance = 10 + politeness * 10
        
    #     max_acceleration = 2  
    #     max_deceleration = -5 

    #     acceleration_factor = max_acceleration / self.weight
    #     deceleration_factor = max_deceleration / self.weight

    #     cruising_speed_factor = 0.5 #TODO: shouldn't be a literal but related to the next vehicle's speed
    #     cruising_speed = self.desiredSpeed * cruising_speed_factor

    #     clearSpaceAhead = (vehicleAhead is None)
    #     if clearSpaceAhead:
    #         acceleration_speed = PixelsConverter.convert_speed_to_pixels_per_frames(acceleration_factor)
    #         if self.speed + acceleration_speed <= self.desiredSpeed:
    #             self.speed += acceleration_speed
    #         else:
    #             self.speed = self.desiredSpeed
    #     else:
    #         # distance = self.location.distance_to(vehicleAhead.location)
    #         # if distance <= minimal_distance:
    #         #     if self.speed > cruising_speed:
    #         #         deceleration_speed = PixelsConverter.convert_speed_to_pixels_per_frames(deceleration_factor)
    #         #         if self.speed + deceleration_speed > cruising_speed:
    #         #             self.speed += deceleration_speed
    #         #         else:
    #         #             self.speed = cruising_speed
    #         #     else:
    #         #         self.speed = cruising_speed
    #         v = self.speed
    #         s = self.location.distance_to(vehicleAhead.location) - 20
    #         delta_v = self.speed - vehicleAhead.speed
    #         min_distance = 40
    #         reaction_time = 1
    #         comfortable_deceleration = 4
    #         delta = 4
    #         # Desired minimum gap
    #         s_star = min_distance + v * reaction_time + (v * delta_v) / (2 * (max_acceleration * comfortable_deceleration)**0.5)

    #         # Acceleration
    #         acceleration = max_acceleration * (1 - (v / self.desiredSpeed)**delta - (s_star / s)**2)
    #         self.speed += acceleration * 0.0167


    def accelerateAndBreak(self, vehicleAhead: 'Vehicle', politeness: int):
        """
        Calculates and updates a vehicle's speed according to the road's conditions - other vehicles, hazards, etc.
        """
        minimal_distance = 10 + politeness * 3
        
        max_acceleration = 2  
        # max_deceleration = -5 

        acceleration_factor = max_acceleration / self.weight
        # deceleration_factor = max_deceleration / self.weight

        clearSpaceAhead = (vehicleAhead is None)
        if clearSpaceAhead:
            acceleration_speed = PixelsConverter.convert_speed_to_pixels_per_frames(acceleration_factor)
            if self.speed + acceleration_speed <= self.desiredSpeed:
                self.speed += acceleration_speed
            else:
                self.speed = self.desiredSpeed
        else:
            v = self.speed
            d = self.location.distance_to(vehicleAhead.location) - (self.lengthOffset + vehicleAhead.lengthOffset) #TODO check witch offset to add ?
            delta_v = self.speed - vehicleAhead.speed
            reaction_time = 0.38
            comfortable_deceleration = 3
            delta = 4

            # Desired minimum gap
            s_star = minimal_distance + v * reaction_time + (v * delta_v) / (2 * (max_acceleration * comfortable_deceleration)**0.5)
           
            # Acceleration
            if d > s_star:  # Prevent division by zero
                # if vehicleAhead.speed != 0:
                #     acceleration = max_acceleration * (1 - (v / vehicleAhead.speed)**delta - (s_star / d)**2)
                # else:
                acceleration = max_acceleration * (1 - (v / self.desiredSpeed)**delta - (s_star / d)**2)
            else:
                acceleration = -comfortable_deceleration  # Decelerate if too close
           
            self.speed += acceleration * 0.0167


            # if vehicleAhead.speed > self.speed:
            #     self.speed = vehicleAhead.speed - PixelsConverter.convert_speed_to_pixels_per_frames(5)

            # Ensure speed is not negative
            self.speed = max(self.speed, 0)




#---------------------Car---------------------#
class Car(Vehicle):
    def __init__(self, location : Vector2, directionIndex : int, laneIndex : int, driveAngle : float, image : Surface, speed=60):
        self.colorIndex = random.randint(0, 4)
        speedCoefficient = normal(CAR_AVG_SPEED, CAR_STANDARD_DEVIATION)
        super().__init__(location, speedCoefficient, directionIndex, laneIndex, driveAngle, image, weight=2, width=20, length=30, speed=speed)
    
    
    
    
    
    
#--------------------Truck--------------------#
class Truck(Vehicle):
    def __init__(self, location : Vector2, directionIndex : int, laneIndex : int, driveAngle : float, image : Surface, speed=60):
        weight = normal(20, 3)
        speedCoefficient = normal(TRUCK_AVG_SPEED, TRUCK_STANDARD_DEVIATION)
        super().__init__(location, speedCoefficient, directionIndex, laneIndex, driveAngle, image, weight=weight, width=20, length=60, speed=speed)
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
        self.finishedSwitchingLane = False
        self.driveAngle = driveAngle
        self.frontEdgeOfVehicle = self.location + Vector2(1, 0).rotate(self.driveAngle) * self.lengthOffset
        self.backEdgeOfVehicle = self.location + Vector2(1, 0).rotate(self.driveAngle + 180) * self.lengthOffset
        self.rightEdgeOfVehicle = self.location + Vector2(1, 0).rotate(self.driveAngle + 90) * self.widthOffset
        self.leftEdgeOfVehicle = self.location + Vector2(1, 0).rotate(self.driveAngle -90) * self.widthOffset
        self.edges = [self.frontEdgeOfVehicle, self.backEdgeOfVehicle, self.rightEdgeOfVehicle, self.leftEdgeOfVehicle]
        self.originalImage = image
        self.rotatedImage = self.originalImage
        self.rect = image.get_rect()

        
    def update_vehicle_edges(self):
        self.frontEdgeOfVehicle = self.location + Vector2(1, 0).rotate(self.driveAngle) * self.lengthOffset
        self.backEdgeOfVehicle = self.location + Vector2(1, 0).rotate(self.driveAngle + 180) * self.lengthOffset
        self.rightEdgeOfVehicle = self.location + Vector2(1, 0).rotate(self.driveAngle + 90) * self.widthOffset
        self.leftEdgeOfVehicle = self.location + Vector2(1, 0).rotate(self.driveAngle -90) * self.widthOffset
        self.edges = [self.frontEdgeOfVehicle, self.backEdgeOfVehicle, self.rightEdgeOfVehicle, self.leftEdgeOfVehicle]

        
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
        
        if self.finishedSwitchingLane:
            self.finishedSwitchingLane = False
            self.shouldSwitchLane = False
        else:
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
            if self.desiredSpeed > vehicleAhead.speed:
                desiredSpeed = PixelsConverter.convert_pixels_per_frames_to_speed(self.desiredSpeed)
                vehicleAheadSpeed = PixelsConverter.convert_pixels_per_frames_to_speed(vehicleAhead.speed)
                difference = desiredSpeed - vehicleAheadSpeed
                if difference >= 10:
                    distanceToVehicleAhead = self.frontEdgeOfVehicle.distance_to(vehicleAhead.backEdgeOfVehicle)
                    if distanceToVehicleAhead < 80:
                        shouldSwitchLane = True


        return shouldSwitchLane
    
    
    def switch_lane(self, vehicleAhead : 'Vehicle', vehiclesLeft : list['Vehicle'], vehiclesRight : list['Vehicle'], road : Road):
        """
        Actively switch lanes. This method determines to which lane the vehicle should move and set a course to that lane
        """
        if self.activelySwitchingLane:
            distanceToTarget = self.location.distance_to(road.get_target_position(self.directionIndex, self.desiredLaneIndex, self.targetPositionIndex))
            if distanceToTarget < 5:
                targetPosition = road.get_target_position(self.directionIndex, self.desiredLaneIndex, self.targetPositionIndex)
                self.location.update(targetPosition)
                self.update_vehicle_edges()
                self.currentLaneIndex = self.desiredLaneIndex
                self.activelySwitchingLane = False
                self.finishedSwitchingLane = True
            return
        else: 
            leftLaneIndex = road.get_left_adjacent_lane_index(self.directionIndex, self.currentLaneIndex)
            rightLaneIndex = road.get_right_adjacent_lane_index(self.directionIndex, self.currentLaneIndex)
            if leftLaneIndex is None and rightLaneIndex is None:
                self.shouldSwitchLane = False
            elif leftLaneIndex is not None and rightLaneIndex is not None:
                pass    # if speed > other vehicle speed: left
                        # else: right (keep right lane is a priority unless passing someone)
            elif leftLaneIndex == None: # can move only to the right lane
                self.check_for_space_in_target_lane(vehiclesRight, vehicleAhead, road, rightLaneIndex, isLeftDirection=False)
            else: # can move to the left lane
                self.check_for_space_in_target_lane(vehiclesLeft, vehicleAhead, road, leftLaneIndex, isLeftDirection=True)

            

    def check_for_space_in_target_lane(self, vehiclesOnSide : list['Vehicle'], vehicleAhead : 'Vehicle', road : Road, targetLaneIndex : int, isLeftDirection : bool):
        switchLane = False
        closestVehicleToSide = self.get_vehicle_ahead(vehiclesOnSide, road, targetLaneIndex)
        distanceToVehicleInFront = self.frontEdgeOfVehicle.distance_to(vehicleAhead.backEdgeOfVehicle)
        
        if closestVehicleToSide is None:          
            # if distanceToVehicleInFront > 80:
            switchLane = True
        else:
            if isLeftDirection:
                distanceToClosestVehicleOnSide = self.location.distance_to(closestVehicleToSide.rightEdgeOfVehicle)
            else:
                distanceToClosestVehicleOnSide = self.location.distance_to(closestVehicleToSide.leftEdgeOfVehicle)
            if distanceToClosestVehicleOnSide > 80:
                # if distanceToVehicleInFront > 80:
                switchLane = True
        
        if switchLane == True:
            self.desiredLaneIndex = targetLaneIndex
            self.activelySwitchingLane = True
            self.targetPositionIndex += int(self.speed) + 1
                        


    
    def update_vehicle_location(self, targetPos: Vector2, speed):
        direction = targetPos - self.location
        desiredAngle = (-math.degrees(math.atan2(direction.y, direction.x))) % 360
        
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
        self.update_vehicle_edges()
            
            
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
        if self.targetPositionIndex <= 1 or targetPosition == self.location:
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
                    leftSideFov = self.create_fov_boundary(direction, -170, -20, 200)                    
                    rightSideFov = self.create_fov_boundary(direction, 20, 170, 200)
                    if self.is_object_in_fov(other_vehicle.edges, frontFov[0], frontFov[1], 200):
                        surroundings['vehicles_front'].append(other_vehicle)
                    if self.is_object_in_fov(other_vehicle.edges, leftSideFov[0], leftSideFov[1], 200):
                        surroundings['vehicles_left'].append(other_vehicle)
                    if self.is_object_in_fov(other_vehicle.edges, rightSideFov[0], rightSideFov[1], 200):
                        surroundings['vehicles_right'].append(other_vehicle)
                
        surroundings['vehicle_ahead'] = self.get_vehicle_ahead(surroundings['vehicles_front'], road, self.desiredLaneIndex)
        return surroundings
    

    #TODO move to calculations ?
    def create_fov_boundary(self, direction : Vector2, leftAngle : float, rightAngle : float, fovDistance : int):
        left_boundary = direction.rotate(leftAngle) * fovDistance
        right_boundary = direction.rotate(rightAngle) * fovDistance
        return (left_boundary, right_boundary)


    def is_object_in_fov(self, objectLocations : list[Vector2], leftBoundary : Vector2, rightBoundary : Vector2, fovDistance : int):
        for location in objectLocations:
            objectToVehicleVector = location - self.location
            cross_left = leftBoundary.cross(objectToVehicleVector)
            cross_right = rightBoundary.cross(objectToVehicleVector)
            if cross_left >= 0 and cross_right <= 0 and objectToVehicleVector.length() <= fovDistance:
                return True
        return False


    def get_vehicle_ahead(self, allVehiclesInFront : list['Vehicle'], road : Road, desiredLaneIndex : int) -> 'Vehicle':
        if len(allVehiclesInFront) == 0:
            return None
        else:
            currentVehicleAhead = None
            minDistance = 0
            first = True
            for vehicle in allVehiclesInFront:
                if self.directionIndex == vehicle.directionIndex:
                    if self.currentLaneIndex == vehicle.currentLaneIndex or self.currentLaneIndex == vehicle.desiredLaneIndex or desiredLaneIndex == vehicle.currentLaneIndex or desiredLaneIndex == vehicle.desiredLaneIndex:
                         #distance = self.location.distance_to(vehicle.location)
                         distance = self.frontEdgeOfVehicle.distance_to(vehicle.backEdgeOfVehicle)
                         if first == True:
                            minDistance = distance
                            currentVehicleAhead = vehicle
                            first = False
                         else:
                             if distance < minDistance:
                                minDistance = distance
                                currentVehicleAhead = vehicle
            return currentVehicleAhead                    
                                
    
    def accelerateAndBreak(self, vehicleAhead: 'Vehicle', politeness: int):
        """
        Calculates and updates a vehicle's speed according to the road's conditions - other vehicles, hazards, etc.
        """
        minimal_distance = 10 + politeness * 3
        
        max_acceleration = 2  
        acceleration_factor = max_acceleration / self.weight

        clearSpaceAhead = (vehicleAhead is None)
        if clearSpaceAhead:
            acceleration_speed = PixelsConverter.convert_speed_to_pixels_per_frames(acceleration_factor)
            if self.speed + acceleration_speed <= self.desiredSpeed:
                self.speed += acceleration_speed
            else:
                self.speed = self.desiredSpeed
        else:
            v = self.speed
            d = self.frontEdgeOfVehicle.distance_to(vehicleAhead.backEdgeOfVehicle)
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
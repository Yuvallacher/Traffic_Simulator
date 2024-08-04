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

CAR_AVG_SPEED = 0.9
CAR_SPEED_STANDARD_DEVIATION = 0.12
TRUCK_AVG_SPEED = 0.8
TRUCK_SPEED_STANDARD_DEVIATION = 0.09
POLITENESS_AVG = 1
POLITENESS_STANDART_DEVIATION = 0.1
AWARENESS_AVG = 1
AWARENESS_STANDART_DEVIATION = 0.1

class Vehicle:
    def __init__(self, location : Vector2, speedCoefficient : float, directionIndex : int, currentLaneIndex : int, driveAngle : float, image : Surface, weight : float, width : int, length : int, speed=60):
        self.location = location
        self.speed = PixelsConverter.convert_speed_to_pixels_per_frames(speed)
        self.desiredSpeed = 0.0
        self.politeness : float
        self.awareness : float
        self.politenessCoefficient = normal(POLITENESS_AVG, POLITENESS_STANDART_DEVIATION)
        self.awarenessCoefficient = normal(AWARENESS_AVG, AWARENESS_STANDART_DEVIATION) #TODO use negatively skewed normal distribution
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
        self.frontEdgeOfVehicle : Vector2
        self.backEdgeOfVehicle : Vector2
        self.rightEdgeOfVehicle : Vector2
        self.leftEdgeOfVehicle : Vector2
        self.edges : list[Vector2]
        self.frontLeftCorner : Vector2
        self.backLeftCorner : Vector2
        self.frontRightcorner : Vector2
        self.backRightCorner : Vector2
        self.corners : list[Vector2]
        self.originalImage = image
        self.rotatedImage = self.originalImage
        self.rect = image.get_rect()
        self.update_vehicle_edges_and_corners()

        
    def update_vehicle_edges_and_corners(self):
        normalizedVector = Vector2(1, 0)
        
        self.frontEdgeOfVehicle = self.location + normalizedVector.rotate(self.driveAngle) * self.lengthOffset
        self.backEdgeOfVehicle = self.location + normalizedVector.rotate(self.driveAngle + 180) * self.lengthOffset
        self.rightEdgeOfVehicle = self.location + normalizedVector.rotate(self.driveAngle + 90) * self.widthOffset
        self.leftEdgeOfVehicle = self.location + normalizedVector.rotate(self.driveAngle -90) * self.widthOffset
        self.edges = [self.frontEdgeOfVehicle, self.backEdgeOfVehicle, self.rightEdgeOfVehicle, self.leftEdgeOfVehicle]
        
        self.frontLeftCorner = self.location + normalizedVector.rotate(self.driveAngle) * self.lengthOffset + normalizedVector.rotate(self.driveAngle - 90) * self.widthOffset
        self.backLeftCorner = self.location + normalizedVector.rotate(self.driveAngle + 180) * self.lengthOffset + normalizedVector.rotate(self.driveAngle - 90) * self.widthOffset
        self.frontRightcorner = self.location + normalizedVector.rotate(self.driveAngle) * self.lengthOffset + normalizedVector.rotate(self.driveAngle + 90) * self.widthOffset
        self.backRightCorner = self.location + normalizedVector.rotate(self.driveAngle + 180) * self.lengthOffset + normalizedVector.rotate(self.driveAngle + 90) * self.widthOffset
        self.corners = [self.frontLeftCorner, self.frontRightcorner, self.backRightCorner, self.backLeftCorner]

        
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
            self.switch_lane(allHazards['vehicle_ahead'], allHazards['vehicles_left'], allHazards['vehicles_right'], road, allHazards['vehicles_front'])
        
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
                if vehicleAheadSpeed == 0:
                    shouldSwitchLane = True
                else:
                    differenceInPercentage = 100 - ((vehicleAheadSpeed / desiredSpeed) * 100)
                    if differenceInPercentage >= 15:
                        #TODO switch this with something that addresses speed and distance, maybe same as s_star? move to seperate function
                        distanceToVehicleAhead = self.frontEdgeOfVehicle.distance_to(vehicleAhead.backEdgeOfVehicle)
                        if distanceToVehicleAhead < 80:
                            shouldSwitchLane = True

        return shouldSwitchLane
    
    
    def switching_lane_decision_2(self, vehicleAhead : 'Vehicle', vehiclesInFront : list['Vehicle'], targetLaneIndex : int) -> bool: #TODO Change function name
        shouldSwitchLane = False
        closestFrontVehicleOnAdjacentLane = self.get_closest_vehicle(vehiclesInFront, targetLaneIndex, "front", checkAllLanes=False)
        if closestFrontVehicleOnAdjacentLane is not None:
            distance = self.frontEdgeOfVehicle.distance_to(closestFrontVehicleOnAdjacentLane.backEdgeOfVehicle)
            otherLaneVehicleSpeed = PixelsConverter.convert_pixels_per_frames_to_speed(closestFrontVehicleOnAdjacentLane.speed)
            vehicleAheadSpeed = PixelsConverter.convert_pixels_per_frames_to_speed(vehicleAhead.speed)              
            if otherLaneVehicleSpeed == 0:
                return shouldSwitchLane
            else:
                differenceInPercentage = 100 - ((vehicleAheadSpeed / otherLaneVehicleSpeed) * 100)
                # speedDifference = otherLaneVehicleSpeed - vehicleAheadSpeed
                #TODO switch this with something that addresses speed and distance, maybe same as s_star? move to seperate function
                if differenceInPercentage > 10 and distance > 120:
                    shouldSwitchLane = True
        else:
            shouldSwitchLane = True
        return shouldSwitchLane                        
                                
    
    def switch_lane(self, vehicleAhead : 'Vehicle', vehiclesLeft : list['Vehicle'], vehiclesRight : list['Vehicle'], road : Road, vehiclesInFront : list['Vehicle']):
        """
        Actively switch lanes. This method determines to which lane the vehicle should move and set a course to that lane
        """
        if self.activelySwitchingLane:
            distanceToTarget = self.location.distance_to(road.get_target_position(self.directionIndex, self.desiredLaneIndex, self.targetPositionIndex))
            if distanceToTarget < 5:
                targetPosition = road.get_target_position(self.directionIndex, self.desiredLaneIndex, self.targetPositionIndex)
                self.location.update(targetPosition)
                self.update_vehicle_edges_and_corners()
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
                if self.switching_lane_decision_2(vehicleAhead, vehiclesInFront, rightLaneIndex):
                    self.check_for_space_in_target_lane(vehiclesRight, vehicleAhead, rightLaneIndex, isLeftDirection=False)
            else: # can move to the left lane
                if self.switching_lane_decision_2(vehicleAhead, vehiclesInFront, leftLaneIndex):
                    self.check_for_space_in_target_lane(vehiclesLeft, vehicleAhead, leftLaneIndex, isLeftDirection=True)

            

    def check_for_space_in_target_lane(self, vehiclesOnSide : list['Vehicle'], vehicleAhead : 'Vehicle', targetLaneIndex : int, isLeftDirection : bool):
        switchLane = False
        direction = 'left' if isLeftDirection else 'right'
        closestVehicleToSide = self.get_closest_vehicle(vehiclesOnSide, targetLaneIndex, direction, checkAllLanes=True)
        distanceToVehicleInFront = self.frontEdgeOfVehicle.distance_to(vehicleAhead.backEdgeOfVehicle)
        
        if closestVehicleToSide is None:          
            # if distanceToVehicleInFront > 80:
            switchLane = True
        else:
            if isLeftDirection:
                distanceToClosestVehicleOnSide = self.leftEdgeOfVehicle.distance_to(closestVehicleToSide.rightEdgeOfVehicle)
            else:
                distanceToClosestVehicleOnSide = self.rightEdgeOfVehicle.distance_to(closestVehicleToSide.leftEdgeOfVehicle)
            
            #TODO switch this with something that depends on politeness
            if distanceToClosestVehicleOnSide > 70:
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
        self.update_vehicle_edges_and_corners()
            
            
    def rotate_vehicle(self):
        self.rotatedImage = transform.rotate(self.originalImage, self.driveAngle)
        self.rect = self.rotatedImage.get_rect(center=self.location)
         
    
    def set_desired_speed(self, maxSpeed : int):
        self.desiredSpeed = PixelsConverter.convert_speed_to_pixels_per_frames(self.speedCoefficient * maxSpeed)
   
    def setPoliteness(self, politeness : int):
        self.politeness = self.politenessCoefficient * politeness
        
    def set_awareness(self, awareness):
        self.awareness = self.awarenessCoefficient * awareness
        if self.awareness > 1:
            self.awareness = 1
        
    
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
                    # for corner in other_vehicle.corners:
                    #     if QuadCalculation.point_in_quad(corner, self.corners):
                    if not (self.inAccident and other_vehicle.inAccident):
                        dataManager.log_accident(type(self).__name__, type(other_vehicle).__name__, PixelsConverter.convert_pixels_per_frames_to_speed(self.speed), PixelsConverter.convert_pixels_per_frames_to_speed(other_vehicle.speed))
                    self.inAccident = True
                    self.speed = 0
                    self.desiredSpeed = 0
                    other_vehicle.inAccident = True
                    other_vehicle.speed = 0
                    other_vehicle.desiredSpeed = 0
                    return surroundings
            
                frontFov = self.create_fov_boundary(direction, -45, 45, 200)
                leftSideFov = self.create_fov_boundary(direction, -170, -20, 200)                    
                rightSideFov = self.create_fov_boundary(direction, 20, 170, 200)
                if self.is_object_in_fov(other_vehicle.corners, frontFov[0], frontFov[1], 200):
                    surroundings['vehicles_front'].append(other_vehicle)
                if self.is_object_in_fov(other_vehicle.corners, leftSideFov[0], leftSideFov[1], 200):
                    surroundings['vehicles_left'].append(other_vehicle)
                if self.is_object_in_fov(other_vehicle.corners, rightSideFov[0], rightSideFov[1], 200):
                    surroundings['vehicles_right'].append(other_vehicle)
                
        surroundings['vehicle_ahead'] = self.get_closest_vehicle(surroundings['vehicles_front'], self.desiredLaneIndex, 'front', checkAllLanes=True)
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


    def get_closest_vehicle(self, allVehiclesInDirection: list['Vehicle'], targetLaneIndex: int, direction: str, checkAllLanes: bool = True) -> 'Vehicle':
        """
        If checkAllLanes == True - returns the closest vehicle on current AND target lanes. 
        Else - returns the closest vehicle on the target lane ONLY
        """
        if len(allVehiclesInDirection) == 0:
            return None
        else:
            currentVehicleInDirection = None
            minDistance = 0
            first = True
            for vehicle in allVehiclesInDirection:
                if direction == 'front':
                    edge = self.frontEdgeOfVehicle
                    otherVehicleEdge = vehicle.backEdgeOfVehicle
                elif direction == 'left':
                    edge = self.leftEdgeOfVehicle
                    otherVehicleEdge = vehicle.rightEdgeOfVehicle
                else:  # direction == 'right'
                    edge = self.rightEdgeOfVehicle
                    otherVehicleEdge = vehicle.leftEdgeOfVehicle

                if self.directionIndex == vehicle.directionIndex:
                    if (checkAllLanes and (self.currentLaneIndex == vehicle.currentLaneIndex or self.currentLaneIndex == vehicle.desiredLaneIndex or targetLaneIndex == vehicle.currentLaneIndex or targetLaneIndex == vehicle.desiredLaneIndex)) or \
                    (not checkAllLanes and targetLaneIndex == vehicle.currentLaneIndex):
                        distance = edge.distance_to(otherVehicleEdge)
                        if first:
                            minDistance = distance
                            currentVehicleInDirection = vehicle
                            first = False
                        else:
                            if distance < minDistance:
                                minDistance = distance
                                currentVehicleInDirection = vehicle
            return currentVehicleInDirection
    
    
    def accelerateAndBreak(self, vehicleAhead: 'Vehicle', politeness: int):
        """
        Calculates and updates a vehicle's speed according to the road's conditions - other vehicles, hazards, etc.
        """
        minimalDistance = 10 + politeness * 3
        
        maxAcceleration = 2  
        accelerationFactor = maxAcceleration / self.weight
        
        clearSpaceAhead = (vehicleAhead is None)
        if clearSpaceAhead:
            accelerationSpeed = PixelsConverter.convert_speed_to_pixels_per_frames(accelerationFactor)
            if self.speed + accelerationSpeed <= self.desiredSpeed:
                self.speed += accelerationSpeed
            else:
                self.speed = self.desiredSpeed
        else:
            distanceToVehicleAhead = self.frontEdgeOfVehicle.distance_to(vehicleAhead.backEdgeOfVehicle)
            speedDifferenceToVehicleAhead = self.speed - vehicleAhead.speed
            reactionTime = 0.38
            comfortableDeceleration = 3
            delta = 4

            safeStoppingDistance = minimalDistance + self.speed * reactionTime + (self.speed * speedDifferenceToVehicleAhead) / (2 * (maxAcceleration * comfortableDeceleration)**0.5)
        
            if distanceToVehicleAhead > safeStoppingDistance: 
                acceleration = maxAcceleration * (1 - (self.speed / self.desiredSpeed)**delta - (safeStoppingDistance / distanceToVehicleAhead)**2)
            else:
                acceleration = -comfortableDeceleration
                if distanceToVehicleAhead < 0.65 * safeStoppingDistance:
                    acceleration -= 0.5 * comfortableDeceleration

            self.speed += acceleration * 0.0167
            
            # # Acceleration
            # if distanceToVehicleAhead > s_star:  # Prevent division by zero
            #     # if vehicleAhead.speed != 0:
            #     #     acceleration = max_acceleration * (1 - (v / vehicleAhead.speed)**delta - (s_star / d)**2)
            #     # else:
            #     acceleration = maxAcceleration * (1 - (self.speed / self.desiredSpeed)**delta - (s_star / distanceToVehicleAhead)**2)
            # else:
            #     acceleration = -comfortableDeceleration  # Decelerate if too close
        
            # self.speed += acceleration * 0.0167


            # if vehicleAhead.speed > self.speed:
            #     self.speed = vehicleAhead.speed - PixelsConverter.convert_speed_to_pixels_per_frames(5)

            # Ensure speed is not negative
            self.speed = max(self.speed, 0)





#---------------------Car---------------------#
class Car(Vehicle):
    def __init__(self, location : Vector2, directionIndex : int, laneIndex : int, driveAngle : float, image : Surface, speed=60):
        self.colorIndex = random.randint(0, 4)
        averageSpeedForLane = CAR_AVG_SPEED - laneIndex * PixelsConverter.convert_speed_to_pixels_per_frames(5)
        speedCoefficient = normal(averageSpeedForLane, CAR_SPEED_STANDARD_DEVIATION)
        super().__init__(location, speedCoefficient, directionIndex, laneIndex, driveAngle, image, weight=2, width=20, length=30, speed=speed)
    
    
    
    
    
    
#--------------------Truck--------------------#
class Truck(Vehicle):
    def __init__(self, location : Vector2, directionIndex : int, laneIndex : int, driveAngle : float, image : Surface, speed=60):
        weight = normal(20, 3)
        averageSpeedForLane = TRUCK_AVG_SPEED - laneIndex * PixelsConverter.convert_speed_to_pixels_per_frames(5)
        speedCoefficient = normal(averageSpeedForLane, TRUCK_SPEED_STANDARD_DEVIATION)
        super().__init__(location, speedCoefficient, directionIndex, laneIndex, driveAngle, image, weight=weight, width=20, length=60, speed=speed)
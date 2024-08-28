from calculations.pixels_calculations import PixelsConverter
from simulation.data.DataManager import DataManager
from simulation.data.Accident import Accident
from simulation.data.Accident import AccidentManager
from simulation.world.hazard import Hazard
from simulation.world.World import World
from simulation.world.World import Road
from numpy.random import normal
from pygame.math import Vector2
from pygame import transform
from pygame import Surface
from pygame import mask
import random
import math
from pygame.draw import line # for debug purposes only

CAR_AVG_SPEED = 0.9
CAR_SPEED_STANDARD_DEVIATION = 0.12
TRUCK_AVG_SPEED = 0.8
TRUCK_SPEED_STANDARD_DEVIATION = 0.09
POLITENESS_AVG = 1
POLITENESS_STANDART_DEVIATION = 0.1
AWARENESS_AVG = 1
AWARENESS_STANDART_DEVIATION = 0.1

class Vehicle:
    def __init__(self, screen, location : Vector2, speedCoefficient : float, roadIndex : int, directionIndex : int, currentLaneIndex : int, driveAngle : float, image : Surface, weight : float, width : int, length : int, speed=60):
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
        self.roadIndex = roadIndex
        self.directionIndex = directionIndex
        self.currentLaneIndex = currentLaneIndex
        self.desiredLaneIndex = self.currentLaneIndex
        self.targetPositionIndex = 0
        self.inJunction = False
        self.desiredJunctionRoadIndex = self.roadIndex
        self.desiredJunctionsDirectionIndex = self.directionIndex
        self.junctionIndex : int
        self.inAccident = False
        self.accident : Accident = None
        self.shouldSwitchLane = False
        self.activelySwitchingLane = False
        self.finishedSwitchingLane = False
        self.encounteredHazards : dict[int, bool] = {}
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
        self.mask = mask.from_surface(self.originalImage) 
        self.update_vehicle_edges_and_corners()
        self.screen = screen
     

        
    def update_vehicle_edges_and_corners(self):
        normalizedVector = Vector2(1, 0)
        coefficient = 1
        if self.driveAngle == 90 or self.driveAngle == 270:
            coefficient *= -1
                        
        self.frontEdgeOfVehicle = (self.location + coefficient * (normalizedVector.rotate(self.driveAngle) * self.lengthOffset))
        self.backEdgeOfVehicle = self.location + coefficient * (normalizedVector.rotate(self.driveAngle + 180) * self.lengthOffset)
        self.rightEdgeOfVehicle = self.location + coefficient * ( normalizedVector.rotate(self.driveAngle + 90) * self.widthOffset)
        self.leftEdgeOfVehicle = self.location + coefficient * (normalizedVector.rotate(self.driveAngle - 90) * self.widthOffset)
        self.edges = [self.frontEdgeOfVehicle, self.backEdgeOfVehicle, self.rightEdgeOfVehicle, self.leftEdgeOfVehicle]
        
        self.frontLeftCorner = self.location + coefficient * (normalizedVector.rotate(self.driveAngle) * self.lengthOffset + normalizedVector.rotate(self.driveAngle - 90) * self.widthOffset)
        self.backLeftCorner = self.location + coefficient * (normalizedVector.rotate(self.driveAngle + 180) * self.lengthOffset + normalizedVector.rotate(self.driveAngle - 90) * self.widthOffset)
        self.frontRightcorner = self.location + coefficient * (normalizedVector.rotate(self.driveAngle) * self.lengthOffset + normalizedVector.rotate(self.driveAngle + 90) * self.widthOffset)
        self.backRightCorner = self.location + coefficient * (normalizedVector.rotate(self.driveAngle + 180) * self.lengthOffset + normalizedVector.rotate(self.driveAngle + 90) * self.widthOffset)
        self.corners = [self.frontLeftCorner, self.frontRightcorner, self.backRightCorner, self.backLeftCorner]

        
    def drive(self, allVehicles : list['Vehicle'], world: World, dataManager : DataManager, accidentManager : AccidentManager, road : Road):
        """
        scan the surroundings, compute the next decision and execute it
        """
        allHazards = self.get_all_hazards_around_vehicle(allVehicles, road, dataManager, accidentManager, world.hazards)
        if not self.inAccident:
            self.make_next_desicion(road, world, allHazards, dataManager)
    
        
    def make_next_desicion(self, road : Road, world : World, allHazards : dict, dataManager : DataManager):
        """
        compute and execute the next decision based on the surroindings
        """
        acceleration = self.calculate_acceleration(allHazards, world.POLITENESS)
        self.accelerate_and_break(acceleration)
        # self.accelerate_and_break(allHazards['vehicle_ahead'], allHazards['hazards_ahead'], world.POLITENESS)
        
        if not self.inJunction:
            if self.finishedSwitchingLane:
                self.finishedSwitchingLane = False
                self.shouldSwitchLane = False
            else:
                self.shouldSwitchLane = self.switching_lane_decision_current_lane(allHazards['vehicle_ahead'])
            
            if self.shouldSwitchLane or self.activelySwitchingLane:
                self.switch_lane(allHazards['vehicle_ahead'], allHazards['vehicles_left'], allHazards['vehicles_right'], road, allHazards['vehicles_front'])
            
            nextTargetPosition = road.get_target_position(self.directionIndex, self.desiredLaneIndex, self.targetPositionIndex + 1)
            startOfJunction, pathOptions, self.junctionIndex = road.is_start_of_junction(nextTargetPosition, self.directionIndex)
            if startOfJunction:
                self.desiredJunctionRoadIndex, self.desiredJunctionsDirectionIndex = self.draw_desired_junction_path(pathOptions)
                self.targetPositionIndex = 0
                self.inJunction = True
                self.set_desired_speed(40)
               
        if self.inJunction:
            nextTargetPosition = road.get_target_position_junction(self.junctionIndex, self.directionIndex, self.desiredJunctionRoadIndex, self.desiredJunctionsDirectionIndex, self.targetPositionIndex + 1)
            endOfJunction, targetPositionIndex = road.is_end_of_junction(nextTargetPosition, self.junctionIndex, self.directionIndex, self.desiredJunctionRoadIndex, self.desiredJunctionsDirectionIndex)
            if endOfJunction:
                self.inJunction = False
                self.targetPositionIndex = targetPositionIndex
                self.roadIndex = int(self.desiredJunctionRoadIndex)
                self.directionIndex = int(self.desiredJunctionsDirectionIndex)
                self.set_desired_speed(world.MAX_SPEED)
        
        self.update_vehicle_location(nextTargetPosition, self.speed) 
        
    
    def get_clear_road_status(self, vehicleAhead : 'Vehicle', hazardsAhead : list[Hazard]) -> list[bool, bool]:
        return vehicleAhead is not None, len(hazardsAhead) != 0
    
    
    def calculate_acceleration(self, allHazards : dict, politeness : int) -> float:
        isVehicleAhead, isHazardAhead = self.get_clear_road_status(allHazards['vehicle_ahead'], allHazards['hazards_ahead'])
        if not isVehicleAhead and not isHazardAhead:
            acceleration = self.acceleration_for_clear_road()
        elif isVehicleAhead and not isHazardAhead:
            acceleration = self.acceleration_for_only_vehicle_ahead(allHazards['vehicle_ahead'], politeness)
        elif not isVehicleAhead and isHazardAhead:
            acceleration = self.acceleration_for_only_hazard_ahead(allHazards['hazards_ahead'])
        else: # isVehicleAhead and isHazardAhead
            acceleration = self.acceleration_for_vehicle_and_hazard(allHazards['vehicle_ahead'], allHazards['hazards_ahead'], politeness)
        return acceleration
    
    
    def acceleration_for_clear_road(self) -> float:
        comfortableDeceleration = 3
        maxAcceleration = 2  
        accelerationFactor = maxAcceleration / self.weight
        
        accelerationSpeed = PixelsConverter.convert_speed_to_pixels_per_frames(accelerationFactor)
        if self.speed > self.desiredSpeed:
            return -comfortableDeceleration * 0.0167
        elif self.speed + accelerationSpeed <= self.desiredSpeed:
            return accelerationSpeed 
        else:
            return (self.desiredSpeed - self.speed) 
    

    def acceleration_for_only_vehicle_ahead(self, vehicleAhead : 'Vehicle', politeness : int) -> float:
        minimalDistance = 10 + politeness * 3
        comfortableDeceleration = 3 
        maxAcceleration = 2  
        reactionTime = 0.38 * self.awareness
        delta = 4

        distanceToVehicleAhead = self.frontEdgeOfVehicle.distance_to(vehicleAhead.backEdgeOfVehicle)
        speedDifferenceToVehicleAhead = self.speed - vehicleAhead.speed
                
        safeStoppingDistance = minimalDistance + self.speed * reactionTime + (self.speed * speedDifferenceToVehicleAhead) / (2 * (maxAcceleration * comfortableDeceleration)**0.5)
    
        if distanceToVehicleAhead > safeStoppingDistance:
            acceleration = maxAcceleration * (1 - (self.speed / self.desiredSpeed)**delta - (safeStoppingDistance / distanceToVehicleAhead)**2)
        else:
            acceleration = -comfortableDeceleration
            if distanceToVehicleAhead < 0.65 * safeStoppingDistance:
                acceleration -= 0.5 * comfortableDeceleration

        return acceleration
        
    
    def acceleration_for_only_hazard_ahead(self, hazardsAhead : list[Hazard]) -> float:
        closestHazard, distanceToHazardAhead = self.get_closest_high_priority_hazard(hazardsAhead)
        acceleration = closestHazard.affect_vehicle(self, distanceToHazardAhead)
        if (closestHazard.type == 'speedLimit') or (closestHazard.type == 'trafficLight' and closestHazard.attributes["isGreenLight"]): #TODO think about yellow light
            print(type(closestHazard)) 
            acceleration = self.acceleration_for_clear_road()
        if closestHazard.type == 'stopSign' or (closestHazard.type == 'trafficLight' and closestHazard.attributes["isRedLight"]): #TODO think about yellow light:
            if distanceToHazardAhead > 40:
                acceleration = self.acceleration_for_clear_road()
        hazardCompletionStatus = closestHazard.check_hazard_rule_completion(self, distanceToHazardAhead)
        self.update_encountered_hazard_status(closestHazard.id, hazardCompletionStatus)
        return acceleration
    
    
    def acceleration_for_vehicle_and_hazard(self, vehicleAhead : 'Vehicle', hazardsAhead : list[Hazard], politeness : int) -> float:
        closestHazard, distanceToHazardAhead = self.get_closest_high_priority_hazard(hazardsAhead)
        if closestHazard.priority == 1:
            self.acceleration_for_only_hazard_ahead(hazardsAhead)
            acceleration = self.acceleration_for_only_vehicle_ahead(vehicleAhead, politeness)
        else:
            distanceToVehicleAhead = self.frontEdgeOfVehicle.distance_to(vehicleAhead.backEdgeOfVehicle)
            if distanceToHazardAhead < distanceToVehicleAhead:
                acceleration = self.acceleration_for_only_hazard_ahead(hazardsAhead)
            else:
                acceleration = self.acceleration_for_only_vehicle_ahead(vehicleAhead, politeness)
        return acceleration
    
    
    def update_encountered_hazard_status(self, hazardID : int, hazardCompletionStatus : bool):
        if hazardID not in self.encounteredHazards.keys():
            self.encounteredHazards[hazardID] = False 
        else:
            self.encounteredHazards[hazardID] = hazardCompletionStatus
        
    
    def draw_desired_junction_path(self, pathOptions : dict) -> list[str, str]:
        keys = list(pathOptions.keys())
        numberOfOptions = len(keys)
        chosenKeyIndex = random.randint(0, numberOfOptions - 1)
        return keys[chosenKeyIndex].strip("[]").split(",")
    
    
    def calculate_safe_distance(self, baseDistance: float) -> float:
        """
        calculates a distance depending on politness and awarness
        """
        return (baseDistance + self.politeness * 5) * self.awareness


    def switching_lane_decision_current_lane(self, vehicleAhead : 'Vehicle') -> bool:
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
                        distanceToVehicleAhead = self.frontEdgeOfVehicle.distance_to(vehicleAhead.backEdgeOfVehicle)
                        if distanceToVehicleAhead < self.calculate_safe_distance(30):
                            shouldSwitchLane = True

        return shouldSwitchLane
    

    def switching_lane_decision_adjacent_lane(self, vehicleAhead : 'Vehicle', vehiclesInFront : list['Vehicle'], targetLaneIndex : int) -> bool: #TODO Change function name
        shouldSwitchLane = False
        closestFrontVehicleOnAdjacentLane = self.get_closest_vehicle_on_same_road(vehiclesInFront, targetLaneIndex, "front", checkAllLanes=False)
        if closestFrontVehicleOnAdjacentLane is not None:
            distance = self.frontEdgeOfVehicle.distance_to(closestFrontVehicleOnAdjacentLane.backEdgeOfVehicle)
            otherLaneVehicleSpeed = PixelsConverter.convert_pixels_per_frames_to_speed(closestFrontVehicleOnAdjacentLane.speed)
            vehicleAheadSpeed = PixelsConverter.convert_pixels_per_frames_to_speed(vehicleAhead.speed)              
            if otherLaneVehicleSpeed == 0:
                return shouldSwitchLane
            else:
                differenceInPercentage = 100 - ((vehicleAheadSpeed / otherLaneVehicleSpeed) * 100)
                if differenceInPercentage > 10 and distance > self.calculate_safe_distance(30):
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
            leftLaneIndex = road.get_left_adjacent_lane_index(self.currentLaneIndex)
            rightLaneIndex = road.get_right_adjacent_lane_index(self.directionIndex, self.currentLaneIndex)
            if leftLaneIndex is None and rightLaneIndex is None:
                self.shouldSwitchLane = False
            # elif leftLaneIndex is not None and rightLaneIndex is not None:
            #     pass    # if speed > other vehicle speed: left
            #             # else: right (keep right lane is a priority unless passing someone)
            elif leftLaneIndex == None: # can move only to the right lane
                if self.switching_lane_decision_adjacent_lane(vehicleAhead, vehiclesInFront, rightLaneIndex):
                    self.check_for_space_in_target_lane(vehiclesRight, vehicleAhead, rightLaneIndex, isLeftDirection=False)
            else: # can move to the left lane
                if self.switching_lane_decision_adjacent_lane(vehicleAhead, vehiclesInFront, leftLaneIndex):
                    self.check_for_space_in_target_lane(vehiclesLeft, vehicleAhead, leftLaneIndex, isLeftDirection=True)

            

    def check_for_space_in_target_lane(self, vehiclesOnSide : list['Vehicle'], vehicleAhead : 'Vehicle', targetLaneIndex : int, isLeftDirection : bool):
        switchLane = False
        direction = 'left' if isLeftDirection else 'right'
        closestVehicleToSide = self.get_closest_vehicle_on_same_road(vehiclesOnSide, targetLaneIndex, direction, checkAllLanes=True)
        distanceToVehicleInFront = self.frontEdgeOfVehicle.distance_to(vehicleAhead.backEdgeOfVehicle)
        
        if closestVehicleToSide is None:          
            # if distanceToVehicleInFront > 80:
            switchLane = True
        else:
            if isLeftDirection:
                distanceToClosestVehicleOnSide = self.leftEdgeOfVehicle.distance_to(closestVehicleToSide.rightEdgeOfVehicle)
            else:
                distanceToClosestVehicleOnSide = self.rightEdgeOfVehicle.distance_to(closestVehicleToSide.leftEdgeOfVehicle)
            
            if distanceToClosestVehicleOnSide > self.calculate_safe_distance(40):
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
        self.mask = mask.from_surface(self.rotatedImage) 

    
    def check_collision(self, other_vehicle : 'Vehicle'):
        offset = (other_vehicle.rect.left - self.rect.left, other_vehicle.rect.top - self.rect.top)
        return self.mask.overlap(other_vehicle.mask, offset) is not None         
    
    def set_desired_speed(self, maxSpeed : int):
        self.desiredSpeed = PixelsConverter.convert_speed_to_pixels_per_frames(self.speedCoefficient * maxSpeed)
   
    def set_politeness(self, politeness : int):
        self.politeness = self.politenessCoefficient * politeness
        
    def set_awareness(self, awareness):
        self.awareness = self.awarenessCoefficient * awareness
        if self.awareness > 1:
            self.awareness = 1
        
    
    def recieve_fov_lines(self, road : Road, angle1 : int, angle2 : int):
        targetPosition = road.get_target_position(self.directionIndex, self.currentLaneIndex, self.targetPositionIndex)
        if not (self.targetPositionIndex <= 1 or targetPosition == self.location):
            direction = (self.location - targetPosition).normalize()
            return self.create_fov_boundary(direction, angle1, angle2, 200)
    
    
    def get_all_hazards_around_vehicle(self, allVehicles : list['Vehicle'], road : Road, dataManager : DataManager, accidentManager : AccidentManager, hazards : list[Hazard]) -> dict:
        """
        The vehicle scans its sorroundings for hazards, oncoming traffic, and other variables that can influence the driver's decision
        """
        surroundings = {}
        surroundings['vehicles_front'] = []
        surroundings['vehicles_left'] = []
        surroundings['vehicles_right'] = []
        surroundings['vehicle_ahead'] = None
        surroundings['hazards_ahead'] = []
        
        targetPosition = road.get_target_position(self.directionIndex, self.currentLaneIndex, self.targetPositionIndex)
        if self.targetPositionIndex <= 1 or targetPosition == self.location:
            return surroundings
        direction = (self.location - targetPosition).normalize()

        frontFov = self.create_fov_boundary(direction, -45, 45, 200)
        leftSideFov = self.create_fov_boundary(direction, -170, -20, 200)                    
        rightSideFov = self.create_fov_boundary(direction, 20, 170, 200)
        #TODO: more checks for surroundings like hazards, turns, etc.
        
        for otherVehicle in allVehicles:
            if self != otherVehicle:
                if self.check_collision(otherVehicle): 
                    if not (self.inAccident and otherVehicle.inAccident):
                        self.handle_accident(otherVehicle, dataManager, accidentManager)
                    return surroundings
                
                if self.is_object_in_fov(otherVehicle.corners, frontFov[0], frontFov[1], 200):
                    surroundings['vehicles_front'].append(otherVehicle)
                if self.is_object_in_fov(otherVehicle.corners, leftSideFov[0], leftSideFov[1], 200):
                    surroundings['vehicles_left'].append(otherVehicle)
                if self.is_object_in_fov(otherVehicle.corners, rightSideFov[0], rightSideFov[1], 200):
                    surroundings['vehicles_right'].append(otherVehicle)
            
        # drawings of fovs - DELETE LATER
        line(self.screen, (255, 0, 0), self.frontEdgeOfVehicle, (self.frontEdgeOfVehicle + frontFov[0]), 1)
        line(self.screen, (255, 0, 0), self.frontEdgeOfVehicle, (self.frontEdgeOfVehicle + frontFov[1]), 1)
        
        # line(self.screen, (0, 0, 255), self.rightEdgeOfVehicle, (self.rightEdgeOfVehicle + rightSideFov[0]), 1)
        # line(self.screen, (0, 0, 255), self.rightEdgeOfVehicle, (self.rightEdgeOfVehicle + rightSideFov[1]), 1)
        
        # line(self.screen, (0, 255, 0), self.leftEdgeOfVehicle, (self.leftEdgeOfVehicle + leftSideFov[0]), 1)
        # line(self.screen, (0, 255, 0), self.leftEdgeOfVehicle, (self.leftEdgeOfVehicle + leftSideFov[1]), 1)
        for hazard in hazards:
            rect = hazard.images[0].get_rect(topleft=(hazard.location.x, hazard.location.y))
            hazardCorners = [
                (rect.left, rect.top),     # Top-left corner
                (rect.right, rect.top),    # Top-right corner
                (rect.left, rect.bottom),  # Bottom-left corner
                (rect.right, rect.bottom)  # Bottom-right corner
            ]
            if self.is_object_in_fov(hazardCorners, frontFov[0], frontFov[1], 150):
                if self.roadIndex == hazard.roadIndex and self.directionIndex == hazard.directionIndex:
                    if hazard.id not in self.encounteredHazards.keys() or self.encounteredHazards[hazard.id] == False:
                        surroundings['hazards_ahead'].append(hazard)       

        surroundings['vehicle_ahead'] = self.get_closest_vehicle_on_same_road(surroundings['vehicles_front'], self.desiredLaneIndex, 'front', checkAllLanes=True)
        return surroundings

    def handle_accident(self, otherVehicle : 'Vehicle', dataManager : DataManager, accidentManager : AccidentManager):
        if self.inAccident:
            self.accident.vehicles.append(otherVehicle)
            otherVehicle.accident = self.accident
        elif otherVehicle.inAccident:
            otherVehicle.accident.vehicles.append(self)
            self.accident = otherVehicle.accident
        else:
            newAccident = accidentManager.add_accident()
            newAccident.vehicles.append(self)
            newAccident.vehicles.append(otherVehicle)
            self.accident = newAccident
            otherVehicle.accident = newAccident
        
        dataManager.log_accident(type(self).__name__, type(otherVehicle).__name__, PixelsConverter.convert_pixels_per_frames_to_speed(self.speed), PixelsConverter.convert_pixels_per_frames_to_speed(otherVehicle.speed), self.accident.id)
        self.inAccident = True
        self.speed = 0
        self.desiredSpeed = 0
        otherVehicle.inAccident = True
        otherVehicle.speed = 0
        otherVehicle.desiredSpeed = 0

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


    def get_closest_vehicle_on_same_road(self, allVehiclesInFovDirection: list['Vehicle'], targetLaneIndex: int, direction: str, checkAllLanes: bool = True) -> 'Vehicle':
        """
        If checkAllLanes == True - returns the closest vehicle on current AND target lanes. 
        Else - returns the closest vehicle on the target lane ONLY
        """
        if len(allVehiclesInFovDirection) == 0:
            return None
        else:
            currentVehicleInDirection = None
            minDistance = 0
            first = True
            for vehicle in allVehiclesInFovDirection:
                if direction == 'front':
                    edge = self.frontEdgeOfVehicle
                    otherVehicleEdge = vehicle.backEdgeOfVehicle
                elif direction == 'left':
                    edge = self.leftEdgeOfVehicle
                    otherVehicleEdge = vehicle.rightEdgeOfVehicle
                else:  # direction == 'right'
                    edge = self.rightEdgeOfVehicle
                    otherVehicleEdge = vehicle.leftEdgeOfVehicle

                if self.roadIndex == vehicle.roadIndex and self.directionIndex == vehicle.directionIndex:
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
    
    
    # def accelerate_and_break(self, vehicleAhead: 'Vehicle', hazardsAhead : list[Hazard], politeness: int):
    #     """
    #     Calculates and updates a vehicle's speed according to the road's conditions - other vehicles, hazards, etc.
    #     """
    #     minimalDistance = 10 + politeness * 3 
        
    #     comfortableDeceleration = 3 
    #     maxAcceleration = 2  
    #     accelerationFactor = maxAcceleration / self.weight
        
    #     noVehicleAhead = vehicleAhead is None
    #     noHazardAhead = len(hazardsAhead) == 0
    #     clearSpaceAhead = noVehicleAhead and noHazardAhead
    #     if not noHazardAhead:
    #         closestHazard, distanceToHazardAhead = self.get_closest_high_priority_hazard(hazardsAhead)
    #         if closestHazard.priority == 1:
    #             clearSpaceAhead = noVehicleAhead
    #             if closestHazard.type == "speedLimit":
    #                 if distanceToHazardAhead <= 50:
    #                     self.set_desired_speed(closestHazard.attributes["limit"])
 
    #     if clearSpaceAhead: # Open road - no hazards and no vehicles ahead
    #         accelerationSpeed = PixelsConverter.convert_speed_to_pixels_per_frames(accelerationFactor)
    #         if self.speed > self.desiredSpeed:
    #             self.speed += -comfortableDeceleration * 0.0167
    #         elif self.speed + accelerationSpeed <= self.desiredSpeed:
    #             self.speed += accelerationSpeed
    #         else:
    #             self.speed = self.desiredSpeed
    #     else:
    #         if not noVehicleAhead and not noHazardAhead:
    #             distanceToVehicleAhead = self.frontEdgeOfVehicle.distance_to(vehicleAhead.backEdgeOfVehicle)
    #             closestHazard, distanceToHazardAhead = self.get_closest_high_priority_hazard(hazardsAhead)
    #             distanceToObjectAhead = min(distanceToVehicleAhead, distanceToHazardAhead)
    #             if distanceToObjectAhead == distanceToHazardAhead:
    #                 speedDifferenceToObjectAhead =  self.speed
    #             #     if closestHazard.type == "stopSign":
    #             #         deceleration = self.calculate_deceleration(distanceToObjectAhead, self.speed)
    #             #         self.speed += deceleration
    #             #         return     
    #             else:
    #                 speedDifferenceToObjectAhead = self.speed - vehicleAhead.speed
    #         elif not noVehicleAhead:
    #             distanceToObjectAhead = self.frontEdgeOfVehicle.distance_to(vehicleAhead.backEdgeOfVehicle)
    #             speedDifferenceToObjectAhead = self.speed - vehicleAhead.speed
    #         elif not noHazardAhead:
    #             closestHazard, distanceToObjectAhead = self.get_closest_high_priority_hazard(hazardsAhead)
    #             if closestHazard.type == "stopSign":
    #                 distanceToStopSign = self.frontEdgeOfVehicle.distance_to(closestHazard.location)
    #                 deceleration = self.calculate_deceleration(distanceToStopSign, self.speed)
    #                 self.speed += deceleration
    #                 return      
    #             speedDifferenceToObjectAhead = self.speed
            
            
    #         reactionTime = 0.38 * self.awareness
    #         delta = 4

    #         safeStoppingDistance = minimalDistance + self.speed * reactionTime + (self.speed * speedDifferenceToObjectAhead) / (2 * (maxAcceleration * comfortableDeceleration)**0.5)
        
    #         if distanceToObjectAhead > safeStoppingDistance: 
    #             acceleration = maxAcceleration * (1 - (self.speed / self.desiredSpeed)**delta - (safeStoppingDistance / distanceToObjectAhead)**2)
    #         else:
    #             acceleration = -comfortableDeceleration
    #             if distanceToObjectAhead < 0.65 * safeStoppingDistance:
    #                 acceleration -= 0.5 * comfortableDeceleration

    #         self.speed += acceleration
            
    #         # Ensure speed is not negative
    #         self.speed = max(self.speed, 0)
    
    
    def accelerate_and_break(self, acceleration : float):
        self.speed += acceleration
        self.speed = max(self.speed, 0) # Ensure speed is not negative
    
          
    def decelerate_to_stop(self, distance, speed) -> float:
        if distance == 0:
            return float('inf')  # Prevent division by zero
        deceleration = -(speed ** 2) / (2 * distance)
        return deceleration
    
    def get_closest_high_priority_hazard(self, hazards : list[Hazard]) -> list[Hazard, float]:
        firstIteration = True
        for hazard in hazards:
            if firstIteration:
                firstIteration = False
                closestHazard = hazard
                distanceToClosestHazard = self.get_minimal_distance_to_corner_of_hazard(hazard)
            else:
                minimalDistanceToCurrentHazard = self.get_minimal_distance_to_corner_of_hazard(hazard)
                if (hazard.priority > closestHazard.priority) or ((hazard.priority == closestHazard.priority) and (minimalDistanceToCurrentHazard < distanceToClosestHazard)):
                    closestHazard = hazard
                    distanceToClosestHazard = minimalDistanceToCurrentHazard
        return hazard, distanceToClosestHazard


    def get_minimal_distance_to_corner_of_hazard(self, hazard : Hazard):
        rect = hazard.images[0].get_rect(topleft=(hazard.location.x, hazard.location.y))
        hazardCorners = [
            (rect.left, rect.top),     # Top-left corner
            (rect.right, rect.top),    # Top-right corner
            (rect.left, rect.bottom),  # Bottom-left corner
            (rect.right, rect.bottom)  # Bottom-right corner
        ]
        distanceToClosestHazard = min([self.frontEdgeOfVehicle.distance_to(corner) for corner in hazardCorners])
        return distanceToClosestHazard

    # def get_vehicle_state(self, )

#---------------------Car---------------------#
class Car(Vehicle):
    def __init__(self, screen, location : Vector2, roadIndex : int, directionIndex : int, laneIndex : int, driveAngle : float, image : Surface, speed=60):
        self.colorIndex = random.randint(0, 4)
        averageSpeedForLane = CAR_AVG_SPEED - laneIndex * PixelsConverter.convert_speed_to_pixels_per_frames(3)
        speedCoefficient = normal(averageSpeedForLane, CAR_SPEED_STANDARD_DEVIATION)
        super().__init__(screen, location, speedCoefficient, roadIndex, directionIndex, laneIndex, driveAngle, image, weight=2, width=20, length=30, speed=speed)
    
    
    
    
    
    
#--------------------Truck--------------------#
class Truck(Vehicle):
    def __init__(self, screen, location : Vector2, roadIndex : int, directionIndex : int, laneIndex : int, driveAngle : float, image : Surface, speed=60):
        weight = normal(20, 3)
        averageSpeedForLane = TRUCK_AVG_SPEED - laneIndex * PixelsConverter.convert_speed_to_pixels_per_frames(3)
        speedCoefficient = normal(averageSpeedForLane, TRUCK_SPEED_STANDARD_DEVIATION)
        super().__init__(screen, location, speedCoefficient, roadIndex, directionIndex, laneIndex, driveAngle, image, weight=weight, width=20, length=60, speed=speed)
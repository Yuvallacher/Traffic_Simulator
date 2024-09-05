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
    def __init__(self, id : int, screen, location : Vector2, speedCoefficient : float, roadIndex : int, directionIndex : int, currentLaneIndex : int, driveAngle : float, image : Surface, weight : float, width : int, length : int, speed=60):
        self.id = id
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
        self.junctionTargetPositionIndex = 0
        self.enterJunction = False
        self.inJunction = False
        self.inJunction = False
        self.desiredJunctionRoadIndex = self.roadIndex
        self.desiredJunctionsDirectionIndex = self.directionIndex
        self.turnDirection : str = ""
        self.junctionID : int = None
        self.inAccident = False
        self.accident : Accident = None
        self.shouldSwitchLane = False
        self.activelySwitchingLane = False
        self.finishedSwitchingLane = False
        self.completedHazards : dict[int, bool] = {}
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
        self.screen = screen #TODO DELETEEEEEEEEEEEEEEEEEEEEEEEE
        self.roundaboutTargetPositionIndex = 0
        self.desiredRoadIndex = self.roadIndex
        self.desiredDirectionIndex = self.directionIndex
        self.roundaboutId : int = None
        self.inRoundabout = False
        self.enteringRoundabout = False
        self.exitingRoundabout = False
        self.canEnterRoundabout = False

        self.waitingToEnterRoundabout = False
        self.stoppingPoint : Vector2 = None

    def update_vehicle_edges_and_corners(self):
        normalizedVector = Vector2(1, 0)
                                
        self.frontEdgeOfVehicle = (self.location + (normalizedVector.rotate(-self.driveAngle) * self.lengthOffset))
        self.backEdgeOfVehicle = self.location + (normalizedVector.rotate(-self.driveAngle + 180) * self.lengthOffset)
        self.rightEdgeOfVehicle = self.location + ( normalizedVector.rotate(-self.driveAngle + 90) * self.widthOffset)
        self.leftEdgeOfVehicle = self.location + (normalizedVector.rotate(-self.driveAngle - 90) * self.widthOffset)
        self.edges = [self.frontEdgeOfVehicle, self.backEdgeOfVehicle, self.rightEdgeOfVehicle, self.leftEdgeOfVehicle]
        
        self.frontLeftCorner = self.location + (normalizedVector.rotate(-self.driveAngle) * self.lengthOffset + normalizedVector.rotate(-self.driveAngle - 90) * self.widthOffset)
        self.backLeftCorner = self.location + (normalizedVector.rotate(-self.driveAngle + 180) * self.lengthOffset + normalizedVector.rotate(-self.driveAngle - 90) * self.widthOffset)
        self.frontRightcorner = self.location + (normalizedVector.rotate(-self.driveAngle) * self.lengthOffset + normalizedVector.rotate(-self.driveAngle + 90) * self.widthOffset)
        self.backRightCorner = self.location + (normalizedVector.rotate(-self.driveAngle + 180) * self.lengthOffset + normalizedVector.rotate(-self.driveAngle + 90) * self.widthOffset)
        self.corners = [self.frontLeftCorner, self.frontRightcorner, self.backRightCorner, self.backLeftCorner]

        
    def drive(self, allVehicles : list['Vehicle'], world: World, dataManager : DataManager, accidentManager : AccidentManager, road : Road):
        """
        scan the surroundings, compute the next decision and execute it
        """
        allHazards = self.get_all_hazards_around_vehicle(allVehicles, road, dataManager, accidentManager, world.hazards)
        if not self.inAccident:
            self.make_next_desicion(road, world, allHazards)
    
        
    def make_next_desicion(self, road : Road, world : World, allHazards : dict):
        """
        compute and execute the next decision based on the surroindings
        """
        acceleration = self.calculate_acceleration(allHazards, world.POLITENESS, world.FPS, road)
        self.accelerate_and_break(acceleration)

        
        if not self.enterJunction and not self.inRoundabout and not self.enteringRoundabout and not self.exitingRoundabout:
            if self.finishedSwitchingLane:
                self.finishedSwitchingLane = False
                self.shouldSwitchLane = False
            else:
                self.shouldSwitchLane = self.switching_lane_decision_current_lane(allHazards['vehicle_ahead'])
            
            if self.shouldSwitchLane or self.activelySwitchingLane:
                self.switch_lane(allHazards['vehicle_ahead'], allHazards['vehicles_left'], allHazards['vehicles_right'], road, allHazards['vehicles_front'])
            
            nextTargetPosition = road.get_target_position(self.directionIndex, self.desiredLaneIndex, self.targetPositionIndex + 1)
            startOfJunction, pathOptions, self.junctionID = road.is_start_of_junction(nextTargetPosition, self.directionIndex)
            
            if startOfJunction:
                self.prepare_to_enter_junction(road, pathOptions, world.maxSpeed)
            else:
                self.check_if_can_enter_roundabout(nextTargetPosition, road)

        
        if self.enteringRoundabout:
            nextTargetPosition = self.entering_roundabout(road, world.maxSpeed)
        elif self.inRoundabout:
            nextTargetPosition = self.in_roundabout(road)
        elif self.exitingRoundabout:
            nextTargetPosition = self.exiting_roundabout(road, world.maxSpeed)
        elif self.enterJunction:
            nextTargetPosition = self.drive_in_junction(road, world, allHazards)
        
        self.update_vehicle_location(nextTargetPosition, self.speed) 
        
    
    def prepare_to_enter_junction(self, road : Road, pathOptions : dict, maxSpeed: float):
        self.desiredJunctionRoadIndex, self.desiredJunctionsDirectionIndex, self.turnDirection = self.draw_desired_junction_path(pathOptions)
        self.junctionTargetPositionIndex = 0
        self.enterJunction = True 
        road.junctions[self.junctionID].add_to_queue(self.id)
        self.set_desired_speed(maxSpeed*0.65)
    
    
    def check_if_can_enter_roundabout(self, nextTargetPosition : Vector2, road : Road):
        if not self.inRoundabout and not self.exitingRoundabout and not self.enteringRoundabout and self.stoppingPoint is None:
            checkTargetPosition = road.get_target_position(self.directionIndex, self.desiredLaneIndex, self.targetPositionIndex + 4)
            isCloseToRoundabout, roundaboutId = road.is_roundabout_entry_point(checkTargetPosition, self.directionIndex)
            if isCloseToRoundabout:
                self.roundaboutId = roundaboutId
                self.stoppingPoint = checkTargetPosition
        isRoundaboutEntryPoint, roundaboutId = road.is_roundabout_entry_point(nextTargetPosition, self.directionIndex)
        if isRoundaboutEntryPoint:
            self.enteringRoundabout = True
            self.roundaboutId = roundaboutId
            self.draw_roundabout_exit_choice(road, self.roundaboutId)
    
    
    def entering_roundabout(self, road : Road, maxSpeed: float) -> Vector2:
        nextTargetPosition = self.handle_roundabout_entry(road, self.roundaboutId)
        if road.is_turn_integrates_roundabout(nextTargetPosition, self.roundaboutId, self.directionIndex):
            self.roundaboutTargetPositionIndex = road.get_roundabout_entering_index(self.roundaboutId, self.directionIndex)
            self.inRoundabout = True
            self.enteringRoundabout = False
            self.set_desired_speed(maxSpeed*0.65)
        return nextTargetPosition
    
    
    def in_roundabout(self, road : Road) -> Vector2:
        nextTargetPosition = road.get_next_target_position_of_roundabout_path(self.roundaboutId, self.roundaboutTargetPositionIndex + 1)        
        if road.is_desired_roundabout_exit_point(self.roundaboutId, nextTargetPosition, self.desiredRoadIndex, self.desiredDirectionIndex):
            self.roundaboutTargetPositionIndex = 0
            self.exitingRoundabout = True
            self.inRoundabout = False
        return nextTargetPosition
    
    
    def exiting_roundabout(self, road : Road, maxSpeed : float) -> Vector2:
        nextTargetPosition = road.get_next_target_position_of_roundabout_exit(self.roundaboutId, self.roundaboutTargetPositionIndex, self.desiredRoadIndex, self.desiredDirectionIndex)
        if road.is_end_of_roundabout_exit(self.roundaboutId, nextTargetPosition, self.desiredRoadIndex, self.desiredDirectionIndex):
            self.targetPositionIndex = road.get_roundabout_to_road_index(self.roundaboutId, self.desiredRoadIndex, self.desiredDirectionIndex)
            self.roadIndex = int(self.desiredRoadIndex)
            self.directionIndex = int(self.desiredDirectionIndex)
            self.exitingRoundabout = False
            self.set_desired_speed(maxSpeed)
        return nextTargetPosition
    
    
    def drive_in_junction(self, road : Road, world : World, allHazards : dict) -> Vector2:
        if self.inJunction:
            nextTargetPosition = road.get_target_position_junction(self.junctionID, self.directionIndex, self.desiredJunctionRoadIndex, self.desiredJunctionsDirectionIndex, self.junctionTargetPositionIndex + 1)
            nextTargetPosition2 = road.get_target_position_junction(self.junctionID, self.directionIndex, self.desiredJunctionRoadIndex, self.desiredJunctionsDirectionIndex, self.junctionTargetPositionIndex + 2)
            endOfJunction, targetPositionIndex = road.is_end_of_junction(nextTargetPosition2, self.junctionID, self.directionIndex, self.desiredJunctionRoadIndex, self.desiredJunctionsDirectionIndex)
            if endOfJunction:
                road.junctions[self.junctionID].remove_from_queue(self.id)
                self.enterJunction = False
                self.inJunction = False
                self.junctionID = None
                self.targetPositionIndex = targetPositionIndex
                self.roadIndex = int(self.desiredJunctionRoadIndex)
                self.directionIndex = int(self.desiredJunctionsDirectionIndex)
                self.set_desired_speed(world.maxSpeed)
        else:
            self.inJunction = self.can_enter_junction(allHazards['vehicles_front'], allHazards['vehicles_right'], allHazards['vehicles_left'], self.turnDirection, road, world.roads)
            nextTargetPosition = road.get_target_position_junction(self.junctionID, self.directionIndex, self.desiredJunctionRoadIndex, self.desiredJunctionsDirectionIndex, self.junctionTargetPositionIndex)
            self.speed = 0 #TODO cahnge to a more gradient stop
        return nextTargetPosition
    
    
    def get_clear_road_status(self, vehicleAhead : 'Vehicle', hazardsAhead : list[Hazard]) -> list[bool, bool]:
        return vehicleAhead is not None, len(hazardsAhead) != 0
    
    
    def calculate_acceleration(self, allHazards : dict, politeness : int, fps : int, road : Road) -> float:
        # === Added ===
        isVehicleAhead, isHazardAhead = self.get_clear_road_status(allHazards['vehicle_ahead'], allHazards['hazards_ahead'])
        if not isVehicleAhead and not isHazardAhead:
            if self.stoppingPoint is not None:
                if self.can_enter_roundabout(road, allHazards['vehicles_left'], allHazards['vehicles_front'], self.roundaboutId):
                    self.canEnterRoundabout = True
                    acceleration = self.acceleration_for_clear_road(fps)
                else:
                    distanceFromStoppingPoint = self.location.distance_to(self.stoppingPoint)
                    acceleration = self.decelerate_to_stop(distanceFromStoppingPoint, self.speed)      
            else:            
                acceleration = self.acceleration_for_clear_road(fps)
        elif isVehicleAhead and not isHazardAhead:
            if self.stoppingPoint is not None:
                if allHazards['vehicle_ahead'].inRoundabout or allHazards['vehicle_ahead'].enteringRoundabout:
                    if self.can_enter_roundabout(road, allHazards['vehicles_left'], allHazards['vehicles_front'], self.roundaboutId):
                        self.canEnterRoundabout = True
                        acceleration = self.acceleration_for_only_vehicle_ahead(allHazards['vehicle_ahead'], politeness, fps)
                    else:
                        distanceFromStoppingPoint = self.location.distance_to(self.stoppingPoint)
                        acceleration = self.decelerate_to_stop(distanceFromStoppingPoint, self.speed)
                else:
                    acceleration = self.acceleration_for_only_vehicle_ahead(allHazards['vehicle_ahead'], politeness, fps)        
            else:
                if self.enteringRoundabout:
                    if self.can_enter_roundabout(road, allHazards['vehicles_left'], allHazards['vehicles_front'], self.roundaboutId) or self.canEnterRoundabout:
                        acceleration = self.acceleration_for_only_vehicle_ahead(allHazards['vehicle_ahead'], politeness, fps)
                        self.canEnterRoundabout = True
                    else:
                        self.speed = 0
                        acceleration = 0    
                else:    
                    acceleration = self.acceleration_for_only_vehicle_ahead(allHazards['vehicle_ahead'], politeness, fps)
        elif not isVehicleAhead and isHazardAhead:
            acceleration = self.acceleration_for_only_hazard_ahead(allHazards['hazards_ahead'], fps)
        else: # isVehicleAhead and isHazardAhead
            acceleration = self.acceleration_for_vehicle_and_hazard(allHazards['vehicle_ahead'], allHazards['hazards_ahead'], politeness, fps)

        return acceleration
    
    
    def acceleration_for_clear_road(self, fps : int) -> float:
        comfortableDeceleration = 3
        maxAcceleration = 2  
        accelerationFactor = maxAcceleration / self.weight
        
        accelerationSpeed = PixelsConverter.convert_speed_to_pixels_per_frames(accelerationFactor)
        if self.speed > self.desiredSpeed:
            return -comfortableDeceleration / fps
        elif self.speed + accelerationSpeed <= self.desiredSpeed:
            return accelerationSpeed
        else:
            return (self.desiredSpeed - self.speed) 
    

    def acceleration_for_only_vehicle_ahead(self, vehicleAhead : 'Vehicle', politeness : int, fps : int) -> float:
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

        return acceleration / fps
        
    
    def acceleration_for_only_hazard_ahead(self, hazardsAhead : list[Hazard], fps : int) -> float:
        closestHazard, distanceToHazardAhead = self.get_closest_high_priority_hazard(hazardsAhead)
        acceleration = closestHazard.affect_vehicle(self, distanceToHazardAhead)
        if (closestHazard.type == 'speedLimit') or (closestHazard.type == 'trafficLight' and closestHazard.attributes["isGreenLight"]): #TODO think about yellow light
            acceleration = self.acceleration_for_clear_road(fps)
        if closestHazard.type == 'stopSign' or (closestHazard.type == 'trafficLight' and closestHazard.attributes["isRedLight"]): #TODO think about yellow light:
            if distanceToHazardAhead > 40:
                acceleration = self.acceleration_for_clear_road(fps)
        hazardCompletionStatus = closestHazard.check_hazard_rule_completion(self, distanceToHazardAhead)
        self.update_encountered_hazard_status(closestHazard.id, hazardCompletionStatus)
        return acceleration
    
    
    def acceleration_for_vehicle_and_hazard(self, vehicleAhead : 'Vehicle', hazardsAhead : list[Hazard], politeness : int, fps : int) -> float:
        closestHazard, distanceToHazardAhead = self.get_closest_high_priority_hazard(hazardsAhead)
        if closestHazard.priority == 1:
            self.acceleration_for_only_hazard_ahead(hazardsAhead, fps)
            acceleration = self.acceleration_for_only_vehicle_ahead(vehicleAhead, politeness, fps)
        else:
            distanceToVehicleAhead = self.frontEdgeOfVehicle.distance_to(vehicleAhead.backEdgeOfVehicle)
            if distanceToHazardAhead < distanceToVehicleAhead:
                acceleration = self.acceleration_for_only_hazard_ahead(hazardsAhead, fps)
            else:
                acceleration = self.acceleration_for_only_vehicle_ahead(vehicleAhead, politeness, fps)
        return acceleration
    
    
    def update_encountered_hazard_status(self, hazardID : int, hazardCompletionStatus : bool):
        if hazardID not in self.completedHazards.keys():
            self.completedHazards[hazardID] = False 
        else:
            self.completedHazards[hazardID] = hazardCompletionStatus


    def handle_roundabout_entry(self, road : Road, roundaboutId : int) -> Vector2:
        nextTargetPosition = road.get_roundabout_entry_target_position(self.roundaboutTargetPositionIndex, roundaboutId, self.directionIndex)
        return Vector2(nextTargetPosition)

    # === Added ===
    def can_enter_roundabout(self, road : Road, vehiclesLeft : list['Vehicle'], vehiclesFront : list['Vehicle'], roundaboutId : int) -> bool:
        direction = Vector2(1, 0).rotate(-self.driveAngle)
        rightRoundaboutEnterFov = self.create_fov_boundary(direction, 10, 60, 50)
        line(self.screen, (255, 0, 0), self.frontEdgeOfVehicle, (self.frontEdgeOfVehicle + rightRoundaboutEnterFov[0]), 1)
        line(self.screen, (255, 0, 0), self.frontEdgeOfVehicle, (self.frontEdgeOfVehicle + rightRoundaboutEnterFov[1]), 1)
        canEnter = True
        for vehicle in vehiclesFront:
            if (vehicle.inRoundabout or vehicle.exitingRoundabout) and roundaboutId == vehicle.roundaboutId:
                if vehicle not in vehiclesLeft:
                    if self.location.distance_to(vehicle.location) < 120:
                        if not self.is_object_in_fov(vehicle.corners, rightRoundaboutEnterFov[0], rightRoundaboutEnterFov[1], 50):
                            canEnter = False
                            self.waitingToEnterRoundabout = True
                            break
        for vehicle in vehiclesLeft:
            if (vehicle.inRoundabout or vehicle.enteringRoundabout or vehicle.exitingRoundabout or vehicle.canEnterRoundabout) and roundaboutId == vehicle.roundaboutId:
                if self.location.distance_to(vehicle.location) < 170:
                    if not self.can_enter_roundabout_in_traffic_jam(vehicle):
                        canEnter = False
                        self.waitingToEnterRoundabout = True
                        break
        return canEnter
    # === Added ===

    def can_enter_roundabout_in_traffic_jam(self, vehicle : 'Vehicle'):
        if vehicle.inRoundabout:
            if vehicle.speed == 0 and self.location.distance_to(vehicle.location) > 15:
                return True
            else:
                return False
        else:
            return True     

    def can_enter_junction(self, frontFOV : list['Vehicle'], rightFOV : list['Vehicle'], leftFOV : list['Vehicle'], turnDirection : str, road : Road, allRoads : list[Road]) -> bool:
        """
        Checks if a vehicle can safetly enter a junction according to the laws of right-of-way. takes into account the direction of turning, incomming traffic and other factors
        """
        if turnDirection == "R":
            rightOfWay = self.check_right_of_way([leftFOV, frontFOV], road, "<", allRoads)
        elif turnDirection == "S":
            samePriority = self.check_right_of_way([rightFOV], road, "==", allRoads)
            lowerPriority = self.check_right_of_way([rightFOV, frontFOV, leftFOV], road, "<", allRoads)
            rightOfWay = samePriority and lowerPriority
        else: # turnDirection == "L"
            samePriority = self.check_right_of_way([rightFOV, frontFOV], road, "==", allRoads)
            lowerPriority = self.check_right_of_way([rightFOV, frontFOV, leftFOV], road, "<", allRoads)
            rightOfWay = (samePriority or road.is_first_in_junction_queue(self.junctionID, self.id)) and lowerPriority 
        return rightOfWay 
    
    
    def check_right_of_way(self, FOVs: list[list['Vehicle']], road: Road, sign: str, allRoads: list[Road]) -> bool:
        """
        Check right-of-way in one case - either a vehicle has higher priority or it doesn't, according to given method parameters
        """
        haveRightOfWay = True
        priority = road.check_road_and_direction_priority(self.junctionID, self.roadIndex, self.directionIndex)
        junctionPath = road.get_junction_path(self.junctionID, self.directionIndex, self.desiredJunctionRoadIndex, self.desiredJunctionsDirectionIndex)
        for fov in FOVs:
            if not haveRightOfWay:
                break
            for vehicle in fov:
                if not self.check_priority_condition(sign, priority, vehicle, allRoads, self.junctionID, junctionPath):
                    haveRightOfWay = False
                    break         
        return haveRightOfWay

    
    def check_priority_condition(self, sign : str, priority : int, otherVehicle : 'Vehicle', allRoads : list[Road], junctionID : int, junctionPath : list[Vector2]):
        """
        Checks a vehicle's right-of-way status compared to a specific vehicle
        """
        if otherVehicle.junctionID is not None:
            if junctionID == otherVehicle.junctionID:
                otherVehiclePriority = allRoads[otherVehicle.roadIndex].check_road_and_direction_priority(otherVehicle.junctionID, otherVehicle.roadIndex, otherVehicle.directionIndex)
                if otherVehicle.distance_to_junction(otherVehicle.junctionID, allRoads[otherVehicle.roadIndex]) < 3:
                    if otherVehicle.inJunction:
                        otherVehicleJunctionPath = allRoads[otherVehicle.roadIndex].get_junction_path(otherVehicle.junctionID, otherVehicle.directionIndex, otherVehicle.desiredJunctionRoadIndex, otherVehicle.desiredJunctionsDirectionIndex)
                        if self.are_paths_colliding(junctionPath, otherVehicleJunctionPath):
                            return False
                    if sign == "<" and priority < otherVehiclePriority:
                        return False
                    elif sign == "==" and priority == otherVehiclePriority:
                        if self.roadIndex != otherVehicle.roadIndex and self.directionIndex != otherVehicle.directionIndex and self.currentLaneIndex == otherVehicle.currentLaneIndex:
                            return False
        return True

    
    def are_paths_colliding(self, vehicle1Path : list[Vector2], vehicle2Path : list[Vector2]) -> bool:
        """
        Checks if 2 lanes within the same junction cross each-other
        """
        if vehicle1Path[0] != vehicle2Path[0]:
            for point1 in vehicle1Path:
                for point2 in vehicle2Path:
                    if Vector2(point1).distance_to(Vector2(point2)) <= 15:
                        return True
        return False
                        
    
    def distance_to_junction(self, junctionIndex : int, road : Road) -> float:
        if self.inJunction:    
            return 0
        else:
            for i in range(0, 3):
                nextTargetPosition = road.get_target_position(self.directionIndex, self.currentLaneIndex, self.targetPositionIndex + i)
                startOfJunction, _, myJunctionIndex = road.is_start_of_junction(nextTargetPosition, self.directionIndex)
                if startOfJunction and myJunctionIndex == junctionIndex:
                    return i
            return float('inf')
    
    
    def draw_roundabout_exit_choice(self, road : Road, roundaboutId : int):
        randomExitNumber = random.randint(0, 3)
        randomExit =  list(road.roundabouts[roundaboutId].exitPaths.keys())
        self.desiredRoadIndex, self.desiredDirectionIndex = randomExit[randomExitNumber].strip("[]").split(",")

    def draw_desired_junction_path(self, pathOptions : dict) -> list[str, str, str]:
        directionKey = list(pathOptions.keys())
        numberOfOptions = len(directionKey)
        desiredPathIndex = random.randint(0, numberOfOptions - 1)
        desiredRoadJunctionIndex, desiredDirectionJunctionIndex = directionKey[desiredPathIndex].strip("[]").split(",")
        turnDirection = pathOptions[f"[{desiredRoadJunctionIndex},{desiredDirectionJunctionIndex}]"][2]
        return desiredRoadJunctionIndex, desiredDirectionJunctionIndex, turnDirection
    
    
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
            switchLane = True
        else:
            if isLeftDirection:
                distanceToClosestVehicleOnSide = self.leftEdgeOfVehicle.distance_to(closestVehicleToSide.rightEdgeOfVehicle)
            else:
                distanceToClosestVehicleOnSide = self.rightEdgeOfVehicle.distance_to(closestVehicleToSide.leftEdgeOfVehicle)
            
            if distanceToClosestVehicleOnSide > self.calculate_safe_distance(40):
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
            if speed == 0: # ===== Added ======
                self.location = self.location
            else: 
                if direction != Vector2(0,0):   
                    direction.scale_to_length(speed)
                    self.location += direction
        else:
            self.location.update(targetPos)
            if self.location == self.stoppingPoint:
                self.stoppingPoint = None
            if not self.enterJunction:
                self.targetPositionIndex += 1
            if self.enterJunction:
                self.junctionTargetPositionIndex += 1
            if self.enteringRoundabout or self.inRoundabout or self.exitingRoundabout:
                self.roundaboutTargetPositionIndex += 1


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
        if not self.enterJunction:
            targetPosition = road.get_target_position(self.directionIndex, self.currentLaneIndex, self.targetPositionIndex)
            if not (self.targetPositionIndex <= 1 or targetPosition == self.location):
                direction = (self.location - targetPosition).normalize()
                return self.create_fov_boundary(direction, angle1, angle2, 200)
        else:
            targetPosition = road.get_target_position(self.directionIndex, self.currentLaneIndex, self.junctionTargetPositionIndex)
            if not (self.junctionTargetPositionIndex <= 1 or targetPosition == self.location):
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
      
        direction = Vector2(1, 0).rotate(-self.driveAngle)
        frontFov = self.create_fov_boundary(direction, -45, 45, 200)
        if self.enterJunction:
            leftSideFov = self.create_fov_boundary(direction, -90, -20, 200)                    
            rightSideFov = self.create_fov_boundary(direction, 20, 90, 200)
        else:
            leftSideFov = self.create_fov_boundary(direction, -170, -20, 200)                    
            rightSideFov = self.create_fov_boundary(direction, 20, 170, 200)

        if self.stoppingPoint is not None and self.enteringRoundabout:
            leftSideFov = self.create_fov_boundary(direction, -100, -20, 170)
            frontFov = self.create_fov_boundary(direction, -45, 20, 170)

        for otherVehicle in allVehicles:
            if self.id != otherVehicle.id:
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
        # line(self.screen, (255, 0, 0), self.frontEdgeOfVehicle, (self.frontEdgeOfVehicle + frontFov[0]), 1)
        # line(self.screen, (255, 0, 0), self.frontEdgeOfVehicle, (self.frontEdgeOfVehicle + frontFov[1]), 1)
        
        # line(self.screen, (0, 0, 255), self.rightEdgeOfVehicle, (self.rightEdgeOfVehicle + rightSideFov[0]), 1)
        # line(self.screen, (0, 0, 255), self.rightEdgeOfVehicle, (self.rightEdgeOfVehicle + rightSideFov[1]), 1)
        
        # line(self.screen, (0, 255, 0), self.leftEdgeOfVehicle, (self.leftEdgeOfVehicle + leftSideFov[0]), 1)
        # line(self.screen, (0, 255, 0), self.leftEdgeOfVehicle, (self.leftEdgeOfVehicle + leftSideFov[1]), 1)
        
        #drawing corners of vehicle - DELETE LATER
        # line(self.screen, (255, 255, 0), self.backRightCorner, self.backLeftCorner, 1)
        # line(self.screen, (255, 255, 0), self.backLeftCorner, self.frontLeftCorner, 1)
        # line(self.screen, (255, 255, 0), self.frontLeftCorner, self.frontRightcorner, 1)
        # line(self.screen, (255, 255, 0), self.frontRightcorner, self.backRightCorner, 1)
        
        
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
                    if hazard.id not in self.completedHazards.keys() or self.completedHazards[hazard.id] == False:
                        surroundings['hazards_ahead'].append(hazard)       

        if not self.enterJunction and not self.inRoundabout and not self.enteringRoundabout:
            nextTargetPosition = road.get_target_position(self.directionIndex, self.currentLaneIndex, self.targetPositionIndex + 1)
            if not road.is_roundabout_entry_point(nextTargetPosition, self.directionIndex)[0]:
                surroundings['vehicle_ahead'] = self.get_closest_vehicle_on_same_road(surroundings['vehicles_front'], self.desiredLaneIndex, 'front', checkAllLanes=True)
            else:
                surroundings['vehicle_ahead'] = self.get_closest_vehicle_in_front_fov(surroundings['vehicles_front'])
        else:
            surroundings['vehicle_ahead'] = self.get_closest_vehicle_in_front_fov(surroundings['vehicles_front'])
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
      
    
    def get_closest_vehicle_in_front_fov(self, vehiclesInFrontFov: list['Vehicle']) -> 'Vehicle':
        if len(vehiclesInFrontFov) == 0:
            return None
        else:
            closestVehicle = vehiclesInFrontFov[0]
            edge = self.frontEdgeOfVehicle
            minDistance = min(edge.distance_to(corner) for corner in vehiclesInFrontFov[0].corners)
            for vehicle in vehiclesInFrontFov:
                distance = min(edge.distance_to(corner) for corner in vehicle.corners)
                if distance < minDistance:
                    minDistance = distance
                    closestVehicle = vehicle
            return closestVehicle
        
    
    def accelerate_and_break(self, acceleration : float):
        self.speed += acceleration
        self.speed = max(self.speed, 0) # Ensure speed is not negative
    
          
    def decelerate_to_stop(self, distance, speed) -> float:
        if distance == 0:
            return float('inf')  # Prevent division by zero
        deceleration = -(speed ** 2) / (2 * distance)
        return deceleration
    
    
    def get_closest_high_priority_hazard(self, hazards : list[Hazard]) -> list[Hazard, float]:
        distanceToClosestHazard = float('inf')
        closestHazard = hazards[0]
        for hazard in hazards:
            distanceToCurrentHazard = self.get_distance_to_hazard(hazard)
            if (hazard.priority > closestHazard.priority) or ((hazard.priority == closestHazard.priority) and (distanceToCurrentHazard < distanceToClosestHazard)):
                closestHazard = hazard
                distanceToClosestHazard = distanceToCurrentHazard
        return hazard, distanceToClosestHazard


    def get_distance_to_hazard(self, hazard : Hazard):
        return self.frontEdgeOfVehicle.distance_to(hazard.lineMidPoint) if hazard.lineMidPoint is not None else float('inf')




#---------------------Car---------------------#
class Car(Vehicle):
    def __init__(self, id : int, screen, location : Vector2, roadIndex : int, directionIndex : int, laneIndex : int, driveAngle : float, image : Surface, speed=60):
        self.colorIndex = random.randint(0, 4)
        averageSpeedForLane = CAR_AVG_SPEED - laneIndex * PixelsConverter.convert_speed_to_pixels_per_frames(3)
        speedCoefficient = normal(averageSpeedForLane, CAR_SPEED_STANDARD_DEVIATION)
        super().__init__(id, screen, location, speedCoefficient, roadIndex, directionIndex, laneIndex, driveAngle, image, weight=2, width=20, length=30, speed=speed)
    
    
    
    
    
    
#--------------------Truck--------------------#
class Truck(Vehicle):
    def __init__(self, id : int, screen, location : Vector2, roadIndex : int, directionIndex : int, laneIndex : int, driveAngle : float, image : Surface, speed=60):
        weight = normal(20, 3)
        averageSpeedForLane = TRUCK_AVG_SPEED - laneIndex * PixelsConverter.convert_speed_to_pixels_per_frames(3)
        speedCoefficient = normal(averageSpeedForLane, TRUCK_SPEED_STANDARD_DEVIATION)
        super().__init__(id, screen, location, speedCoefficient, roadIndex, directionIndex, laneIndex, driveAngle, image, weight=weight, width=20, length=60, speed=speed)
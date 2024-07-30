from simulation.world.World import World
#from simulation.world.Point import Point
from simulation.vehicle.Vehicle import Vehicle
from simulation.vehicle.Vehicle import Car
from simulation.vehicle.Vehicle import Truck
from simulation.world.road import Road
from pygame.math import Vector2
from pygame import Surface
from drawings.vehicle_drawer import VehicleDrawer
import random
import math

TRUCK_PROBABILITY = 0.1

class VehiclesManager:
    
    def __init__(self, max_number_of_cars) -> None:
        self.vehicles : list[Vehicle] = []
        self.maxNumOfCars = max_number_of_cars


    def add_vehicles(self, allLanesInRoad : list[list[Road.Lane]], simulationWorld: World):
        """
        adds at most one new vehicle for each lane
        """
        for direction in allLanesInRoad:
            for lane in direction:
                if len(self.vehicles) < self.maxNumOfCars:
                    if random.uniform(0, 1) >= 1 / (simulationWorld.FREQUENCY * 10):
                        space_available = True
                        for vehicle in self.vehicles:
                            # if vehicle.directionIndex == allLanesInRoad.index(direction) and vehicle.laneIndex == direction.index(lane) and vehicle.location.distance_to(lane.startingPoint) <= 100:
                            if vehicle.directionIndex == allLanesInRoad.index(direction) and vehicle.currentLaneIndex == direction.index(lane):
                                if vehicle.targetPositionIndex <= 4:
                                    # TODO fix distance checking! currently checks in an "air distance" so not entirely accurate
                                    space_available = False
                                    break
                        if space_available:
                            vehicleCoordinates = Vector2(lane.path[0].x, lane.path[0].y)
                            initialDirection = lane.path[1] - vehicleCoordinates
                            driveAngle = -math.degrees(math.atan2(initialDirection.y, initialDirection.x))
                            #coordinates = Vector2(-simulationWorld.maxSpeed, lane.y) # TODO think how to move to start of road 
                            directionIndex = allLanesInRoad.index(direction)
                            laneIndex = direction.index(lane)
                            car_probability = random.uniform(0, 1)
                            if car_probability >= TRUCK_PROBABILITY:
                                image = VehicleDrawer.get_car_image()
                                newVehicle = Car(vehicleCoordinates, directionIndex, laneIndex, driveAngle, image, speed=simulationWorld.MAX_SPEED)
                            else:
                                image = VehicleDrawer.get_truck_image()
                                newVehicle = Truck(vehicleCoordinates, directionIndex, laneIndex, driveAngle, image, speed=simulationWorld.MAX_SPEED)
                            newVehicle.setDesiredSpeed(simulationWorld.MAX_SPEED)
                            self.vehicles.append(newVehicle)
                        
                        
    def remove_vehicles(self, allLanesInRoad : list[list[Road.Lane]]):
        for vehicle in self.vehicles:
            directionIndex = vehicle.directionIndex
            laneIndex = vehicle.currentLaneIndex
            
            if vehicle.location == allLanesInRoad[directionIndex][laneIndex].path[-1]:
                self.vehicles.remove(vehicle)


import simulation.data.Accident
import simulation.data.DataManager
from simulation.world.World import World
from simulation.vehicle.Vehicle import Vehicle
from simulation.vehicle.Vehicle import Car
from simulation.vehicle.Vehicle import Truck
from simulation.world.road import Road
import simulation.data
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
        self.vehicleID = 1


    def add_vehicles(self, simulationWorld: World, screen):
        """
        adds at most one new vehicle for each lane
        """
        allRoads = simulationWorld.roads
        for roadIndex, road in enumerate(allRoads):
            allLanesInRoad = road.allLanesInRoad
            for direction in allLanesInRoad:
                for lane in direction:
                    if lane.spawnPoint:
                        if len(self.vehicles) < self.maxNumOfCars:
                            if random.uniform(0, 1) >= 1 / (simulationWorld.FREQUENCY * 10):
                                space_available = True
                                for vehicle in self.vehicles:
                                    if vehicle.roadIndex == roadIndex and vehicle.directionIndex == allLanesInRoad.index(direction) and vehicle.currentLaneIndex == direction.index(lane):
                                        if vehicle.targetPositionIndex <= World.SPAWN_RATE:
                                            space_available = False
                                            break
                                if space_available:
                                    vehicleCoordinates = Vector2(lane.path[0].x, lane.path[0].y)
                                    initialDirection = lane.path[1] - vehicleCoordinates
                                    driveAngle = -math.degrees(math.atan2(initialDirection.y, initialDirection.x))
                                    directionIndex = allLanesInRoad.index(direction)
                                    laneIndex = direction.index(lane)
                                    car_probability = random.uniform(0, 1)
                                    if car_probability >= TRUCK_PROBABILITY:
                                        image = VehicleDrawer.get_car_image()
                                        newVehicle = Car(self.vehicleID, screen, vehicleCoordinates, roadIndex, directionIndex, laneIndex, driveAngle, image, speed=simulationWorld.MAX_SPEED)
                                    else:
                                        image = VehicleDrawer.get_truck_image()
                                        newVehicle = Truck(self.vehicleID, screen, vehicleCoordinates, roadIndex, directionIndex, laneIndex, driveAngle, image, speed=simulationWorld.MAX_SPEED)
                                    newVehicle.set_desired_speed(simulationWorld.MAX_SPEED)
                                    newVehicle.set_politeness(simulationWorld.POLITENESS)
                                    newVehicle.set_awareness(simulationWorld.AWARENESS)
                                    newVehicle.rotate_vehicle() 
                                    self.vehicles.append(newVehicle)
                                self.vehicleID += 1
                        
                        
    def updateCarPos(self, simulationWorld : World, dataManager : simulation.data.DataManager, accidentManager : simulation.data.Accident): #TODO probably move to a different place
        for vehicle in self.vehicles:
            vehicleRoad = simulationWorld.get_vehicle_road(vehicle.roadIndex)
            vehicle.drive(self.vehicles, simulationWorld, dataManager, accidentManager, vehicleRoad)

    def remove_vehicles(self, roads : list[Road]):

        for vehicle in self.vehicles:
            roadIndex = vehicle.roadIndex
            directionIndex = vehicle.directionIndex
            laneIndex = vehicle.currentLaneIndex
            
            if vehicle.location == roads[roadIndex].allLanesInRoad[directionIndex][laneIndex].path[-1]:
                self.vehicles.remove(vehicle)

from drawings.vehicle_drawer import VehicleDrawer
from simulation.vehicle.Vehicle import Vehicle
from simulation.vehicle.Vehicle import Truck
from simulation.vehicle.Vehicle import Car
from simulation.world.World import World
from simulation.world.road import Road
import simulation.data.DataManager
import simulation.data.Accident
from pygame.math import Vector2
import simulation.data
import random
import math

class VehiclesManager:
    
    def __init__(self, maxNumberOfCars : int, truckPercentage : float) -> None:
        self.vehicles : list[Vehicle] = []
        self.maxNumOfCars = maxNumberOfCars
        self.truckPercentage = truckPercentage
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
                            if random.random() >= 1 / (simulationWorld.FREQUENCY * 10):
                                space_available = True
                                for vehicle in self.vehicles:
                                    if vehicle.roadIndex == roadIndex and vehicle.directionIndex == allLanesInRoad.index(direction) and vehicle.currentLaneIndex == direction.index(lane):
                                        if vehicle.targetPositionIndex <= World.SPAWN_RATE + (10 - road.density):
                                            space_available = False
                                            break
                                if space_available:
                                    vehicleCoordinates = Vector2(lane.path[0].x, lane.path[0].y)
                                    initialDirection = lane.path[1] - vehicleCoordinates
                                    driveAngle = -math.degrees(math.atan2(initialDirection.y, initialDirection.x))
                                    directionIndex = allLanesInRoad.index(direction)
                                    laneIndex = direction.index(lane)
                                    car_probability = random.random()
                                    if car_probability >= self.truckPercentage:
                                        image = VehicleDrawer.get_car_image()
                                        newVehicle = Car(self.vehicleID, screen, vehicleCoordinates, roadIndex, directionIndex, laneIndex, driveAngle, image, speed=simulationWorld.maxSpeed)
                                    else:
                                        image = VehicleDrawer.get_truck_image()
                                        newVehicle = Truck(self.vehicleID, screen, vehicleCoordinates, roadIndex, directionIndex, laneIndex, driveAngle, image, speed=simulationWorld.maxSpeed)
                                    newVehicle.set_desired_speed(simulationWorld.maxSpeed)
                                    newVehicle.set_politeness(simulationWorld.POLITENESS)
                                    newVehicle.set_awareness(simulationWorld.AWARENESS)
                                    newVehicle.rotate_vehicle() 
                                    self.vehicles.append(newVehicle)
                                self.vehicleID += 1
                        
                        
    def updateCarPos(self, simulationWorld : World, dataManager : simulation.data.DataManager, accidentManager : simulation.data.Accident):
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

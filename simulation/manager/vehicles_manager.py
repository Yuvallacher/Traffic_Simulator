from simulation.world.World import World
from simulation.world.Point import Point
from simulation.vehicle.Vehicle import Vehicle
from simulation.vehicle.Vehicle import Car
from simulation.vehicle.Vehicle import Truck
from simulation.world.road import Road
import random

TRUCK_PROBABILITY = 0.1

class VehiclesManager:
    
    def __init__(self, max_number_of_cars) -> None:
        self.vehicles = []
        self.num_of_cars = max_number_of_cars


    def addCar(self, lanes: list[Road.Lane], simulationWorld: World):
        if random.uniform(0, 1) >= 1 / (simulationWorld.frequency * 10):
            if len(self.vehicles) < self.num_of_cars:
                for lane in lanes:
                    space_available = True
                    for vehicle in self.vehicles:
                        if vehicle.lane == lanes.index(lane) and vehicle.location.x <= 100:
                            space_available = False
                            break
                    if space_available:
                        coordinates = Point(-simulationWorld.maxSpeed, lane.y)
                        new_vehicle_lane = simulationWorld.road.getLane(coordinates)
                        car_probability = random.uniform(0, 1)
                        if car_probability >= TRUCK_PROBABILITY:
                            newVehicle = Car(coordinates, new_vehicle_lane, speed=simulationWorld.maxSpeed)
                        else:
                            newVehicle = Truck(coordinates, new_vehicle_lane ,speed=simulationWorld.maxSpeed)
                        newVehicle.setDesiredSpeed(simulationWorld.maxSpeed)
                        self.vehicles.append(newVehicle)
                        
                        
    def removeCars(self, end : int):
        for vehicle in self.vehicles:
            if vehicle.location.x > end:
                self.vehicles.remove(vehicle)


from world.World import World
from world.Point import Point
from vehicle.Vehicle import Vehicle
from vehicle.Vehicle import Car
from vehicle.Vehicle import Truck
import random

class VehiclesManager:
    
    def __init__(self, max_number_of_cars) -> None:
        self.vehicles = []
        self.num_of_cars = max_number_of_cars


    def addCar(self, lanes: list, simulationWorld: World):
        if random.uniform(0, 1) >= 1 / (simulationWorld.frequency * 10):
            if len(self.vehicles) < self.num_of_cars:
                for lane in lanes:
                    space_available = True
                    for vehicle in self.vehicles:
                        if abs(vehicle.location.y - lane) < 5 and vehicle.location.x <= 50:
                            space_available = False
                            break
                    if space_available:
                        car_probability = random.uniform(0, 1)
                        if car_probability >= 0.25:
                            newCar = Car(Point(-simulationWorld.maxSpeed, lane), speed=simulationWorld.maxSpeed)
                            newCar.setDesiredSpeed(simulationWorld.maxSpeed)
                            self.vehicles.append(newCar)
                            break
                        else:
                            newTruck = Truck(Point(-simulationWorld.maxSpeed, lane), speed=simulationWorld.maxSpeed)
                            newTruck.setDesiredSpeed(simulationWorld.maxSpeed)
                            self.vehicles.append(newTruck)
                            break
                        
                        
    def removeCars(self, end : int):
        for vehicle in self.vehicles:
            if vehicle.location.x > end:
                self.vehicles.remove(vehicle)


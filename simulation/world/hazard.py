from pygame.surface import Surface
from pygame.math import Vector2
from abc import ABC, abstractmethod

global id
id = 0
class Hazard:
    def __init__(self, type: str, location: Vector2, roadIndex: int, directionIndex: int, images: list[Surface], attributes: dict, priority: int):
        self.type = type
        self.location = location
        self.roadIndex = roadIndex
        self.directionIndex = directionIndex
        self.images = images
        self.rect = images[0].get_rect(topleft=(location.x, location.y))
        self.attributes = attributes
        self.priority = priority
        self.lineMidPoint : Vector2 = None
        self.lineStart : Vector2 = None
        self.lineEnd : Vector2 = None
        self.drawLine = False
        self.nearJunction = False
        self.junctionID = False
        global id
        self.id = id + 1
        id += 1
        

    @abstractmethod
    def affect_vehicle(self, vehicle, distance: float) -> float:
        """
        Tells the vehicle how it should behave based on the hazard's type and attributes
        """
        pass
    
    @abstractmethod
    def check_hazard_rule_completion(self, vehicle, distance : float) -> bool:
        """
        Tells the vehicle wether it "completed" the hazard's requirements
        """
        pass

    def set_new_position(self, roadIndex : int, directionIndex : int, coordinate : Vector2):
        self.location = coordinate
        self.roadIndex = roadIndex
        self.directionIndex = directionIndex

class SpeedLimit(Hazard):
    def __init__(self, location: Vector2, roadIndex: int, directionIndex: int, images: list[Surface], speed_limit: int):
        super().__init__("speedLimit", location, roadIndex, directionIndex, images, {"limit": speed_limit}, priority=1)

    def affect_vehicle(self, vehicle, distance: float) -> float:
        if distance <= 50:
            vehicle.set_desired_speed(self.attributes["limit"])
        return -10 # for overide

    def check_hazard_rule_completion(self, vehicle, distance : float) -> bool:
        if distance <= 50:
            return True
        return False


class StopSign(Hazard):
    def __init__(self, location: Vector2, roadIndex: int, directionIndex: int, images: list[Surface]):
        super().__init__("stopSign", location, roadIndex, directionIndex, images, {}, priority=2)

    def affect_vehicle(self, vehicle, distance: float) -> float:
        return vehicle.decelerate_to_stop(distance, vehicle.speed)

    def check_hazard_rule_completion(self, vehicle, distance : float) -> bool:
        return distance <= 10 and vehicle.speed <= 0.01


class TrafficLight(Hazard):
    def __init__(self, location: Vector2, roadIndex: int, directionIndex: int, images: list[Surface], color : list[bool]):
        super().__init__("trafficLight", location, roadIndex, directionIndex, images, {"isRedLight": color[0], "isYellowLight": color[1], "isGreenLight": color[2]}, priority=2)
        
    def affect_vehicle(self, vehicle, distance: float) -> float:
        if self.attributes["isRedLight"]:
            return vehicle.decelerate_to_stop(distance, vehicle.speed)
        elif self.attributes["isYellowLight"]:
            pass
        elif self.attributes["isGreenLight"]:
            return -10
        
    def check_hazard_rule_completion(self, vehicle, distance: float) -> bool:
        if distance <= 25:
            if self.attributes["isGreenLight"]:
                return True
            elif self.attributes["isYellowLight"]:
                pass
            else: # self.attributes["isRedLight"]
                return False
        else:
            return False
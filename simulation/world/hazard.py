from pygame.surface import Surface
from pygame.math import Vector2
from abc import ABC, abstractmethod

class Hazard:
    def __init__(self, type: str, location: Vector2, roadIndex: int, directionIndex: int, images: list[Surface], attributes: dict, priority: int):
        self.type = type
        self.location = location
        self.roadIndex = roadIndex
        self.directionIndex = directionIndex
        self.images = images
        self.attributes = attributes
        self.priority = priority

    @abstractmethod
    def affect_vehicle(self, vehicle, distance: float):
        """
        Default behavior if no specific hazard class overrides it.
        Can be overridden by subclasses.
        """
        pass


class SpeedLimit(Hazard):
    def __init__(self, location: Vector2, roadIndex: int, directionIndex: int, images: list[Surface], speed_limit: int):
        super().__init__("speedLimit", location, roadIndex, directionIndex, images, {"limit": speed_limit}, priority=1)

    def affect_vehicle(self, vehicle, distance: float):
        if distance <= 50:
            vehicle.set_desired_speed(self.attributes["limit"])


class StopSign(Hazard):
    def __init__(self, location: Vector2, roadIndex: int, directionIndex: int, images: list[Surface]):
        super().__init__("stopSign", location, roadIndex, directionIndex, images, {}, priority=2)

    def affect_vehicle(self, vehicle, distance: float):
        if distance <= 30:  # Adjust based on desired behavior
            vehicle.decelerate_to_stop(distance)

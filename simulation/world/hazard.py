from pygame.surface import Surface
from pygame.math import Vector2
from gui.inputBox import InputBox
import pygame
from abc import abstractmethod

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
    def __init__(self, location: Vector2, roadIndex: int, directionIndex: int, images: list[Surface], speedLimit: int):
        super().__init__("speedLimit", location, roadIndex, directionIndex, images, {"limit": speedLimit}, priority=1)
        self.inputBox = InputBox(self.rect.centerx - 25, self.rect.centery - 10, 50, 32, pygame.font.Font(None, 18), defaultText=str(speedLimit), drawBorder=False)
        self.inputActive = False

    def affect_vehicle(self, vehicle, distance: float) -> float:
        if distance <= 50:
            vehicle.set_desired_speed(self.attributes["limit"])
        return -10

    def check_hazard_rule_completion(self, vehicle, distance: float) -> bool:
        return distance <= 50

    def draw(self, screen):
        screen.blit(self.images[0], self.rect)
        self.inputBox.rect.topleft = (self.rect.centerx - 12, self.rect.centery - 30)
        self.inputBox.draw(screen)

    def update_input_box_position(self):
        self.inputBox.rect.topleft = (self.rect.centerx - 23, self.rect.centery - 10)

    def set_speed_limit(self, newLimit: float):
        newLimitInt = int(newLimit)
        self.attributes["limit"] = newLimit
        self.inputBox.text = str(newLimitInt)
        self.inputBox.txt_surface = pygame.font.Font(None, 18).render(str(newLimitInt), True, self.inputBox.color)


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
        self.countdown : int = 2
        self.countdownStarted = False


    def affect_vehicle(self, vehicle, distance: float) -> float:
        if self.attributes["isGreenLight"]:
            return -10
        else:
            return vehicle.decelerate_to_stop(distance, vehicle.speed)

        
    def check_hazard_rule_completion(self, vehicle, distance: float) -> bool:
        if distance <= 10:
            return self.attributes["isGreenLight"]
        else:
            return False


    def draw(self, screen):
        if self.attributes["isGreenLight"]:
            screen.blit(self.images[2], self.rect)
        elif self.attributes["isYellowLight"]:
            screen.blit(self.images[1], self.rect)
        else: # self.attributes["isRedLight"]
            screen.blit(self.images[0], self.rect)


    def start_count_down(self):
        if self.attributes["isGreenLight"]:
            self.countdown = 8
        else:
            self.countdown = 2


    def change_color(self):
        if self.attributes["isGreenLight"]:
            self.attributes["isGreenLight"] = 0
            self.attributes["isYellowLight"] = 1
            self.priority = 2
        elif self.attributes["isYellowLight"]:
            self.attributes["isYellowLight"] = 0
            self.attributes["isRedLight"] = 1
            self.priority = 2
        else: # self.attributes["isRedLight"]
            self.attributes["isRedLight"] = 0        
            self.attributes["isGreenLight"] = 1
            self.priority = 1
            
            
class TrafficLightsManager():
    def __init__(self):
        self.trafficLights : list[TrafficLight] = []
        self.activeTrafficLight : TrafficLight = None
        self.activeIndex : int = 0
    
    def add_traffic_light(self, trafficLight : TrafficLight):
        if trafficLight not in self.trafficLights:
            self.trafficLights.append(trafficLight)
        if not self.activeTrafficLight:
            self.activeTrafficLight = trafficLight
            self.activeTrafficLight.countdownStarted = True
        
    def remove_traffic_light(self, trafficLight : TrafficLight):
        if trafficLight in self.trafficLights:
            self.trafficLights.remove(trafficLight)
        if len(self.trafficLights) == 0:
            self.activeTrafficLight = None

    def synchronize_traffic_lights(self, fps : int):
        if self.activeTrafficLight is not None:
            if self.activeTrafficLight.countdownStarted:
                self.activeTrafficLight.countdown -= 1 / fps
                if self.activeTrafficLight.countdown <= 0:
                    self.activeTrafficLight.change_color()
                    self.activeTrafficLight.start_count_down()
                    if self.activeTrafficLight.attributes["isRedLight"]:
                        self.activeTrafficLight.countdownStarted = False
                        self.activeIndex = (self.activeIndex + 1) % len(self.trafficLights)
                        self.activeTrafficLight = self.trafficLights[self.activeIndex]
                        self.activeTrafficLight.countdownStarted = True
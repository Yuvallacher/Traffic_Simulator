from calculations.pixels_calculations import PixelsConverter
from world.Point import Point
from world.World import World
import random
from numpy.random import normal

class Vehicle:
    def __init__(self, location : Point, speed=60):
        self.location = location
        self.coefficient = normal(1, 0.12)
        self.speed = PixelsConverter.convert_speed_to_pixels_per_frames(speed)
        self.desiredSpeed = 0
        self.width = 15
        self.height = 10
        self.colorIndex = random.randint(0, 4)
    
    
    def setDesiredSpeed(self, maxSpeed : int):
        self.desiredSpeed = PixelsConverter.convert_speed_to_pixels_per_frames(self.coefficient * maxSpeed)
    
    
    def checkDistance(self, otherCars, world : World):
        front_of_car = self.location.x + self.width
        car_lane = self.location.y
        minimalDistance = 10 + world.politeness * 5
        
        for other_car in otherCars:
            front_other_car_x = other_car.location.x + other_car.width
            other_car_lane = other_car.location.y
            if car_lane == other_car_lane:
                if front_other_car_x > front_of_car:
                    distance = front_other_car_x - front_of_car
                    if distance < minimalDistance:
                        return False

        return True
    
    
    def accelerateAndBreak(self, otherCars, world : World):
        clearSpaceAhead = self.checkDistance(otherCars, world)
        if clearSpaceAhead:
            if self.speed + PixelsConverter.convert_speed_to_pixels_per_frames(1 + self.speed * 0.1) <= self.desiredSpeed:
                self.speed += PixelsConverter.convert_speed_to_pixels_per_frames(1 + self.speed * 0.1)
            else:
                self.speed = self.desiredSpeed
        else:
            if self.speed - PixelsConverter.convert_speed_to_pixels_per_frames(3) > 0:
                self.speed -= PixelsConverter.convert_speed_to_pixels_per_frames(3)
            else:
                self.speed = 0
    

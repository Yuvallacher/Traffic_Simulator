from calculations.pixels_calculations import PixelsConverter
from world.Point import Point
from world.World import World

class Vehicle:
    def __init__(self, location : Point, speed, diameter):
        self.location = location
        self.speed = PixelsConverter.convert_speed_to_pixels_per_frames
        self.diameter = diameter
        self.width = 15
        self.height = 10
    
    def checkDistance(self, otherCars, world):
        front_x = self.location.x + self.diameter
        
        for other_car in otherCars:
            if other_car.location.x > front_x and other_car.location.x - front_x < 10 + world.politeness * 5:
                return False

        return True
    
    def accelerateAndBreak(self, otherCars, world):
        if self.checkDistance(otherCars, world):
            if self.speed + 0.03 <= world.maxSpeed:
                self.speed += 0.03
        else:
            if self.speed - 0.02 > 0:
                self.speed -= 0.02
                
    def updateDesiredSpeed(self, world : World):
        self.desiredSpeed = self.desiredSpeedCoefficient * world.maxSpeed
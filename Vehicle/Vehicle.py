from calculations.pixels_calculations import PixelsConverter

class Vehicle:
    def __init__(self, xPos, yPos, speed, diameter):
        self.xPos = xPos
        self.yPos = yPos
        self.speed = PixelsConverter.convert_speed_to_pixels_per_frames
        self.diameter = diameter
        self.width = 15
        self.height = 10
    
    def checkDistance(self, otherCars, world):
        front_x = self.xPos + self.diameter
        
        for other_car in otherCars:
            if other_car.xPos > front_x and other_car.xPos - front_x < world.politeness * 10:
                return False
        
        return True
    
    def accelerateAndBreak(self, otherCars, world):
        if self.checkDistance(otherCars, world):
            if self.speed + 0.03 <= world.maxSpeed:
                self.speed += 0.03
        else:
            if self.speed - 0.02 > 0:
                self.speed -= 0.02
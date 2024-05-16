import Point
class Vehicle:
    def __init__(self, point, speed, diameter, world):
        #vehicle position
        self.position = point

        #driver decision
        self.decision = 0

        #speed managment
        if world.maxSpeed <= speed:
            self.speed = world.maxSpeed
            self.intendedSpeed = world.maxSpeed
        else:
            self.speed = speed
            self.intendedSpeed = speed
        self.diameter = diameter

        #lane managment
        self.goToLowerLane = False
        self.goToUpperLane = False
    
    def checkDistance(self, otherCars, world):
        front_x = self.position.x + self.diameter
        
        for other_car in otherCars:
            if other_car.position.x > front_x and (other_car.position.x - front_x) < world.politeness * 10:
                return False
        
        return True
    
    def accelerateAndBreak(self, otherCars, world):
        if self.checkDistance(otherCars, world):
            if self.speed + 0.03 <= world.maxSpeed:
                if self.speed + 0.02 > self.intendedSpeed:
                    self.speed = self.intendedSpeed
                else:
                    self.speed += 0.02
        else:
            if self.speed - 0.02 > 0:
                self.speed -= 0.02
    
    def moveLaneLeft(self, otherCars, world, lane: Point):
        if self.speed < self.intendedSpeed and self.position.y > lane.y:
            self.goToUpperLane = True
            front_x = self.position.x + self.diameter
            back_x = self.position.x - self.diameter
            for car in otherCars:
                if  car.position.x == front_x or car.position.x == back_x:
                    self.goToUpperLane = False
                    
    
    def moveLaneRight(self, otherCars, world, lane: Point):
        if self.speed == self.intendedSpeed and self.position.y < lane.y:
            self.goToLowerLane = True
            front_x = self.position.x + self.diameter
            back_x = self.position.x - self.diameter
            for car in otherCars:
                if  car.position.x == front_x or car.position.x == back_x:
                    self.goToLowerLane = False

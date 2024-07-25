import sympy as sp
from sympy import Expr
from simulation.world.World import World
from simulation.world.road import Road
from simulation.world.Point import Point
import pygame


@staticmethod
def getStraightRoadImg(numberOfLanes: int) -> str:

    listOfStraightRoads = ['straightRoad.png', 'straightRoad2.png', 'straightRoad3.png', 'straightRoad4.png', 'straightRoad.png5',]
    
    if numberOfLanes > len(listOfStraightRoads) or numberOfLanes < 1:
        return None
    return "straightRoadPictures\\" + listOfStraightRoads[numberOfLanes - 1]

class straightRoad:


    def __init__(self, numberOfLanes: int, scale):
        try:
            roadImg = getStraightRoadImg(numberOfLanes= numberOfLanes)
            self.road = pygame.image.load(roadImg)
            self.road = pygame.transform.scale(self.road, scale)
            self.yFunction = False
            self.xFunction = False
        except:
            print("Error! Invalid number of lanes.")

    def setRoadFunctionAsX(self, param: int):
        self.x = param
        self.xFunction = True

    def setRoadFunctionAsY(self, param: int):
        self.y = param
        self.yFunction = True

    def getPoint(self, param: int) -> Point:
        if self.yFunction:
            return Point(param, self.y)
        if self.xFunction:
            return Point(self.x, param)
        return Point(0,0)

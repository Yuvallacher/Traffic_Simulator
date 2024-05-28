
from world.Point import Point
from sympy import Expr

class Road:
    LANE_WIDTH = 40
    def __init__(self ,road_function : Expr, starting_position : Point, ending_position : Point):
        self.starting_position = starting_position
        self.road_y = road_function
        self.ending_position = ending_position


    def get_road_function(self) -> Expr:
        return self.road_y   
    def get_road_starting_pos(self) -> Point:
        return self.starting_position
    def get_road_ending_pos(self) -> Point:
        return self.ending_position
    
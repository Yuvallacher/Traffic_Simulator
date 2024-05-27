import sympy as sp
from sympy import Expr
from world.World import World
from simulation.manager.road import Road
from point import Point

class RoadCalculator:
    NUM_POINTS = 1000  # Number of points to calculate along the function
    VAR_SYMBOL = sp.symbols('x')
    
    # Calculate points along the function
    @staticmethod
    def calculate_road_points( road : Road  ) -> list:
        road_function = road.get_road_function()
        road_starting_point = road.get_road_starting_pos()
        road_ending_point = road.get_road_ending_pos()
        x_start = road_starting_point.get_x_pos()
        x_end = road_ending_point.get_x_pos()
        points = []
        for i in range(RoadCalculator.NUM_POINTS):
            x_value = x_start + (x_end - x_start) * i /RoadCalculator.NUM_POINTS
            y_value = road_function.subs(RoadCalculator.VAR_SYMBOL, x_value)
            points.append((int(World.SCREEN_WIDTH + x_value * 20), int(World.SCREEN_HEIGHT - y_value * 20)))  
        return points    
    
    @staticmethod   
    def calculate_horizontal_road_points(road : Road) -> list:
        road_starting_point = road.get_road_starting_pos()
        y = road_starting_point.get_y_pos()
        num_of_points = World.SCREEN_WIDTH
        points = []
        for i in range(num_of_points):
            points.append((i,y))
        return points    

    @staticmethod
    def calculate_function_by_two_points(point1 : Point, point2 : Point ):
        x, y = sp.symbols('x y')
        x1, y1 = (point1.get_x_pos(), point1.get_y_pos())
        x2, y2 = (point2.get_x_pos(), point2.get_y_pos())    
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        equation = sp.Eq(y, m * x + b) 
        return equation
    
        
      
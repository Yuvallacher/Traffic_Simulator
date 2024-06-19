import pygame
from simulation.world.road import Road
from simulation.world.World import World
from calculations.road_calculation import RoadCalculator
from simulation.world.Point import Point
import sympy as sp

class RoadDrawer:

    @staticmethod
    def draw_road(road : Road):
         # Draw function line
        points = RoadCalculator.calculate_horizontal_road_points(road)
        GRAY = (153, 163, 164)
        WHITE = (255, 255, 255)
        pygame.draw.lines(World.SCREEN, GRAY, False, points, Road.LANE_WIDTH)
        first_point = points[0]
        xPos = first_point[0]
        yPos = first_point[1]
        while xPos <= World.SCREEN_WIDTH :
            pygame.draw.line(World.SCREEN, WHITE, (xPos, yPos), (xPos + 5, yPos), width=3)
            xPos += 10
    
    @staticmethod
    def draw_road_by_two_points(point1 : Point, point2 : Point):
        
        road = Road(RoadCalculator.calculate_function_by_two_points(point1, point2),point1, point2)
        GRAY = (153, 163, 164)
        pygame.draw.line(World.SCREEN, GRAY, (point1.get_x_pos(),point1.get_y_pos()), (point2.get_x_pos(),point2.get_y_pos()), Road.LANE_WIDTH)
        RoadDrawer.lane_seperator(road)
        # equation = RoadCalculator.calculate_function_by_two_points(point1, point2)
        # start_point = point1
        # xPos = start_point.get_x_pos()
        # yPos = start_point.get_y_pos()
        # # y = sp.symbols('y')
        # # while xPos <= World.SCREEN_WIDTH :

        # #     y_value = sp.solve(equation.subs('x', xPos), y)[0]
        # #     pygame.draw.line(World.SCREEN, WHITE, (xPos, yPos), (xPos + 5, yPos), width=3)
        # #     xPos += 10

    def lane_seperator(road : Road):
        equation = road.get_road_function()
        i = road.get_road_starting_pos().get_x_pos()
        y = sp.symbols('y')
        WHITE = (255, 255, 255)
        while i <= World.SCREEN_WIDTH:
            pygame.draw.line(World.SCREEN, WHITE, (i,int(sp.solve(equation.subs('x', i), y)[0])), (i+2,int(sp.solve(equation.subs('x', i + 2), y)[0])),2)
            i += 5
              



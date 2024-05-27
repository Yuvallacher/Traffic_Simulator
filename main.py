import pygame
import time
from World.World import World
from simulation.manager.road import Road
from point import Point
from drawings.road_drawer import RoadDrawer
import sympy as sp


pygame.init()


simulationRunning = True
starting_point = Point(0, World.SCREEN_HEIGHT / 2)
ending_point = Point(World.SCREEN_WIDTH, World.SCREEN_HEIGHT / 2)
world = World(100,2,3.5)
road = Road(world.SCREEN_HEIGHT / 2, starting_point, ending_point)

WHITE = (255, 255, 255)
clock = pygame.time.Clock()
BLACK = (0,0,0)
while simulationRunning:
    world.SCREEN.fill(WHITE)
    RoadDrawer.draw_road_by_two_points(Point(0,0), Point(1080,500))
    #pygame.draw.line(World.SCREEN,BLACK,(0,0),(1080,500),50)
   # RoadDrawer.draw_road(road)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simulationRunning = False
    pygame.display.update()
    clock.tick(60)
    

pygame.quit()
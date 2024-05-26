import pygame
import Vehicle.Vehicle as Vehicle
import random
import time
import Point
import World.World as World
import Road
import math


SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720

#world settings
world = World.World(0.5, 2, 2)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

simulationRunning = True

#colors
GREY = (153, 163, 164)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#lanes
lanes = [307.5, 324]

#frames
clock = pygame.time.Clock()
fps = 300


#cars
cars = []

#arcs:
start_angle = 0  # Start angle in radians
end_angle = 90  # End angle in radians
t = 0

#roads 
# road = pygame.Rect(0, 300, SCREEN_WIDTH, 33)
newRoad = Road.Road('x')

def addCars(frequency, cars):
    for lane in lanes:
        if random.uniform(0, 1) >= 1 / frequency and len(cars) < 5: 
            cars.append(Vehicle.Vehicle(Point.Point(-10, lane), random.uniform(0.1, 2), 2, world))

def switchLanes(cars, lanes: list):
    for car in cars:
        print(car.goToUpperLane)
        if car.goToLowerLane:
            car.position.y = lanes[1]
        if car.goToUpperLane:
            car.position.y = lanes[0]


def drawRoad(screen):
    
    for start, end in zip(newRoad.listOfRoadPoints, newRoad.listOfRoadPoints[1:]):
        pygame.draw.line(screen, WHITE, (start.x, start.y), (end.x, end.y), width=2)
        pygame.draw.rect(screen, GREY, pygame.Rect(start.x, start.y,abs(end.x - start.x), 7))

def calculate_arc_point(rect, start_angle, end_angle, thickness, t):
    # t should be in range [0, 1]
    angle = start_angle + (end_angle - start_angle) * t
    x = rect.centerx + int((rect.width / 2 - thickness / 2) * math.cos(angle))
    y = rect.centery + int((rect.height / 2 - thickness / 2) * math.sin(angle))
    return x, y

# def draw_smooth_arc(surface, color, rect, start_angle, end_angle, thickness):
#     segments = 100  # Number of segments to draw the arc
#     angle_step = (end_angle - start_angle) / segments
    
#     for i in range(segments):
#         angle1 = start_angle + i * angle_step
#         angle2 = start_angle + (i + 1) * angle_step
        
#         # Calculate start and end points of the arc segment
#         x1 = rect.centerx + int((rect.width / 2 - thickness / 2) * math.cos(angle1))
#         y1 = rect.centery + int((rect.height / 2 - thickness / 2) * math.sin(angle1))
#         x2 = rect.centerx + int((rect.width / 2 - thickness / 2) * math.cos(angle2))
#         y2 = rect.centery + int((rect.height / 2 - thickness / 2) * math.sin(angle2))
        
#         # Draw the arc segment
#         pygame.draw.arc(surface, color, rect, angle1, angle2, thickness)
def draw_smooth_arc(surface, color, rect, start_angle, end_angle, thickness):
    segments = 100  # Number of segments to draw the arc
    angle_step = (end_angle - start_angle) / segments
    
    for i in range(segments):
        angle1 = start_angle + i * angle_step
        angle2 = start_angle + (i + 1) * angle_step
        
        # Calculate the rectangle for the arc segment
        arc_segment_rect = pygame.Rect(rect)
        arc_segment_rect.inflate_ip(-thickness // 2, -thickness // 2)
        
        # Draw the arc segment
        pygame.draw.arc(surface, color, arc_segment_rect, angle1, angle2, thickness)




while simulationRunning:
    clock.tick(fps)
    t += 0.0001
    screen.fill(WHITE)
#    pygame.draw.rect(screen, GREY, road)
#    drawRoad(screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simulationRunning = False
    closestCar = 800
    # switchLanes(cars, lanes)
    # for movingCar in cars:
    #     carCoordinate = Point.Point(float(movingCar.position.x,), float(movingCar.position.y,))
    #     movingCar.accelerateAndBreak(cars, world)
    #     movingCar.moveLaneRight(cars, world, Point.Point(0, lanes[1]))
    #     movingCar.moveLaneLeft(cars, world, Point.Point(0, lanes[0]))
    #     movingCar.position.x += movingCar.speed
    #     pygame.draw.circle(screen, BLACK, (carCoordinate.x, carCoordinate.y), 7.5)
    #     closestCar = min(closestCar, movingCar.position.x)
    #     if movingCar.position.x >= SCREEN_WIDTH:
    #         cars.remove(movingCar)
    # if closestCar > 20:
    #     addCars(world.frequency, cars)
    rect = pygame.Rect(150, 100, 500, 600)
    size = 100
    draw_smooth_arc(screen, GREY, rect, math.radians(start_angle), math.radians(end_angle), size)         # 0 to 90 degrees
    draw_smooth_arc(screen, GREY, rect, math.radians(start_angle + 90), math.radians(end_angle + 90), size) # 90 to 180 degrees
    draw_smooth_arc(screen, GREY, rect, math.radians(start_angle + 180), math.radians(end_angle + 180), size) # 180 to 270 degrees
    draw_smooth_arc(screen, GREY, rect, math.radians(start_angle + 270), math.radians(end_angle + 270), size) # 270 to 360 degrees
    x, y = calculate_arc_point(rect, start_angle, end_angle, 100, t)
    pygame.draw.circle(screen, BLACK, (x, y), 10)

    pygame.display.update()
    pygame.display.flip()


pygame.QUIT()


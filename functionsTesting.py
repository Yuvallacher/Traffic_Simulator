# import pygame
# import sys

# # Initialize Pygame
# pygame.init()

# # Set up the display
# WIDTH, HEIGHT = 800, 600
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Dot Following Function Path")

# # Define colors
# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)
# BLUE = (0, 0, 255)
# RED = (255, 0, 0) 

# # Define function parameters
# x_start, x_end = -10, 10  # Define the range of x values
# num_points = 1000  # Number of points to calculate along the function
# dot_radius = 10  # Radius of the dot

# # Calculate points along the function
# points = []
# for i in range(num_points):
#     x = x_start + (x_end - x_start) * i / num_points
#     y = x ** 2  # Function: y = x^2
#     points.append((int(WIDTH / 2 + x * 20), int(HEIGHT - y * 20)))  # Scale and shift points

# # Initialize dot position
# dot_x = points[0][0]
# dot_y = points[0][1]

# # Main loop
# running = True
# clock = pygame.time.Clock()
# index = 0  # Index to track the current point on the function curve
# while running:
#     screen.fill(WHITE)

#     # Draw function line
#     pygame.draw.lines(screen, BLACK, False, points,10)

#     # Draw dot
#     pygame.draw.circle(screen, RED, (dot_x, dot_y), dot_radius)



#     # Move dot along the function path
#     index += 1
#     if index >= len(points):
#         index = 0
#     dot_x, dot_y = points[index]

#     # Event handling
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     # Update display
#     pygame.display.flip()

#     # Cap the frame rate
#     clock.tick(60)

# # Quit Pygame
# pygame.quit()
# sys.exit()
import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 1280, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Object Following a Path")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

PIXELS_PER_METER = 5
FPS = 60
car_speed_kmh = 60
car_speed_mps = car_speed_kmh * 1000 / 3600
car_speed_ppf = car_speed_mps * PIXELS_PER_METER / FPS

# Define the path as a list of (x, y) coordinates
# path = [
#     (0, 300),
#     (300,300), 
#     (500,500),
#     (300, 700),
#     (0, 700)
# ]

# path = [
#     (0, 0),
#     (100,100), 
#     (400,100),
#     (400, 400),
#     (700,400),
#     (700,1000), 
# ]




path = [
(0,400),
(600, 400),
(605.4349399776909, 400.8029610475247),
(609.7955704592144, 403.1212709237777),
(614.0458052323451, 405.7155700710133),
(615.6465430040436, 407.6474949678909),
(618.3512378596722, 410.18659626093),
(619.2896013810126, 412.4497082829865),
(620, 415),
(620,1280)
]




# for i in range(1000):
#     path.append((i,300))





car_image = pygame.image.load('carPictures\\redCar.png')
car_image = pygame.transform.scale(car_image,(25,15))
car_rect = car_image.get_rect()
car_rect.topleft = path[0]


# Object properties
obj_radius = 10
obj_pos = list(path[0])  # Start position
car_pos = list(path[0])
rectangle = pygame.Rect(obj_pos[0], obj_pos[1], 20, 15)

# Create a surface
rect_width, rect_height = 20, 15
rect_surface = pygame.Surface((rect_width, rect_height))
rect_surface.fill(red)

# Get the rectangle of the surface
rect = rect_surface.get_rect() 
rect.center = (obj_pos[0], obj_pos[1])


# Path index and speed
path_index = 0
speed = car_speed_ppf

# Function to move the object towards the next point in the path
def move_object(obj_pos, target_pos, speed):
    direction = pygame.math.Vector2(target_pos) - obj_pos
    distance = direction.length()
    if distance > speed:
        direction.scale_to_length(speed)
        obj_pos[0] += direction.x
        obj_pos[1] += direction.y
    else:
        obj_pos[0], obj_pos[1] = target_pos
    return obj_pos


# Main loop
running = True
clock = pygame.time.Clock()
old_direction = pygame.math.Vector2(path[path_index]) - (car_rect.x,car_rect.y) 
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move object
    if path_index < len(path):
        obj_pos = move_object(obj_pos, path[path_index], speed)
        # rectangle.topleft = (obj_pos[0],obj_pos[1])
        rect.center = (obj_pos[0],obj_pos[1])
        car_rect.x, car_rect.y = move_object( car_pos, path[path_index], speed)
        
        # new_direction = pygame.math.Vector2(path[path_index]) - (car_rect.x,car_rect.y)
        # angle = new_direction.angle_to(old_direction)
        # old_direction = new_direction

        new_direction = (pygame.math.Vector2(path[path_index]) - rect.center)
        # angle = new_direction.angle_to(old_direction)
        angle = -math.degrees(math.atan2(new_direction.y, new_direction.x))
        old_direction = new_direction

        # Rotate the surface
        rotated_surface = pygame.transform.rotate(rect_surface, angle)
    
        # Get the rotated rectangle
        rotated_rect = rotated_surface.get_rect(center=rect.center) 
        
        car_image = pygame.transform.rotate(car_image , angle)
        if obj_pos == list(path[path_index]):
            path_index += 1
      
    # Clear screen
    screen.fill(black)

    # Draw path
    for i in range(len(path) - 1):
        pygame.draw.line(screen, white, path[i], path[i + 1], 40)
    
    screen.blit(car_image, car_rect)
    # Draw object
    # pygame.draw.circle(screen, red, (int(obj_pos[0]), int(obj_pos[1])), obj_radius)
    screen.blit(rotated_surface, rotated_rect.center)

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
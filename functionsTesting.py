import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dot Following Function Path")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0) 

# Define function parameters
x_start, x_end = -10, 10  # Define the range of x values
num_points = 1000  # Number of points to calculate along the function
dot_radius = 10  # Radius of the dot

# Calculate points along the function
points = []
for i in range(num_points):
    x = x_start + (x_end - x_start) * i / num_points
    y = x ** 2  # Function: y = x^2
    points.append((int(WIDTH / 2 + x * 20), int(HEIGHT - y * 20)))  # Scale and shift points

# Initialize dot position
dot_x = points[0][0]
dot_y = points[0][1]

# Main loop
running = True
clock = pygame.time.Clock()
index = 0  # Index to track the current point on the function curve
while running:
    screen.fill(WHITE)

    # Draw function line
    pygame.draw.lines(screen, BLACK, False, points,10)

    # Draw dot
    pygame.draw.circle(screen, RED, (dot_x, dot_y), dot_radius)



    # Move dot along the function path
    index += 1
    if index >= len(points):
        index = 0
    dot_x, dot_y = points[index]

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
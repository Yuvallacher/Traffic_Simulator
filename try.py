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
car_speed_kmh = 120
car_speed_mps = car_speed_kmh * 1000 / 3600
car_speed_ppf = car_speed_mps * PIXELS_PER_METER / FPS

path = [
    (0, 400),
    (600, 400),
    (605.4349399776909, 400.8029610475247),
    (609.7955704592144, 403.1212709237777),
    (614.0458052323451, 405.7155700710133),
    (615.6465430040436, 407.6474949678909),
    (618.3512378596722, 410.18659626093),
    (619.2896013810126, 412.4497082829865),
    (620, 415),
    (620, 1280)
]



car_image = pygame.image.load('carPictures\\redCar.png')
car_image = pygame.transform.scale(car_image, (25, 15))
car_rect = car_image.get_rect()
car_rect.center = path[0]

# Object properties
obj_radius = 10
obj_pos = pygame.math.Vector2(path[0])  # Start position
car_pos = pygame.math.Vector2(path[0])

# Path index and speed
path_index = 0
speed = car_speed_ppf

# Function to move the object towards the next point in the path
def move_object(obj_pos, target_pos, speed):
    direction = target_pos - obj_pos
    distance = direction.length()
    if distance > speed:
        direction.scale_to_length(speed)
        obj_pos += direction
    else:
        obj_pos.update(target_pos)
    return obj_pos

# Main loop
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move object
    if path_index < len(path) - 1:
        target_pos = pygame.math.Vector2(path[path_index + 1])
        car_pos = move_object(car_pos, target_pos, speed)
        obj_pos = move_object(obj_pos, target_pos, speed)

        # Calculate the angle for the car rotation
        direction = target_pos - car_pos
        angle = -math.degrees(math.atan2(direction.y, direction.x))

        # Rotate the car image
        rotated_car_image = pygame.transform.rotate(car_image, angle)
        car_rect = rotated_car_image.get_rect(center=car_pos)

        if car_pos.distance_to(target_pos) < speed:
            path_index += 1

    # Clear screen
    screen.fill(black)

    # Draw path
    for i in range(len(path) - 1):
        pygame.draw.line(screen, white, path[i], path[i + 1], 40)

    # Draw car
    screen.blit(rotated_car_image, car_rect.topleft)

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

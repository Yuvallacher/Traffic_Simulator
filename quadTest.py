from pygame.math import Vector2
from pygame.rect import Rect
from calculations.polygon_calculations import QuadCalculation


rect = Rect(100, 30, 25, 20)

biggerRect = QuadCalculation.create_quad(rect, 2)

print(biggerRect)
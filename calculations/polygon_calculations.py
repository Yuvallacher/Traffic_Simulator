from pygame.math import Vector2
from pygame.rect import Rect

class QuadCalculation:
    @staticmethod
    def point_in_quad(point : Vector2, quad : list[Vector2]) -> bool:
        cp1 = QuadCalculation.cross_product((quad[1] - quad[0]), (point - quad[0]))
        cp2 = QuadCalculation.cross_product((quad[2] - quad[1]), (point - quad[1]))
        cp3 = QuadCalculation.cross_product((quad[3] - quad[2]), (point - quad[2]))
        cp4 = QuadCalculation.cross_product((quad[0] - quad[3]), (point - quad[3]))

        pointInQuad = (cp1 >= 0 and cp2 >= 0 and cp3 >= 0 and cp4 >= 0) or (cp1 <= 0 and cp2 <= 0 and cp3 <= 0 and cp4 <= 0)
        return pointInQuad

    
    @staticmethod    
    def cross_product(v1, v2) -> float:
            return v1[0] * v2[1] - v1[1] * v2[0]


    @staticmethod
    def create_quad(vehicleRect : Rect, driveAngle : float, vehicleSpeed : float) -> list[Vector2]:
        x = 10
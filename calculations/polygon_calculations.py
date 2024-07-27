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
    def create_quad(vehicleRect : Rect, vehicleSpeed : float) -> list[Vector2]:
        front_left = Vector2(vehicleRect.topleft)
        front_right = Vector2(vehicleRect.topright)
        back_left = Vector2(vehicleRect.bottomleft)
        back_right = Vector2(vehicleRect.bottomright)
        
        front_center = (front_left + front_right) / 2
        back_center = (back_left + back_right) / 2
        direction_vector = (front_center - back_center).normalize()
        
        # Width of the field of view should cover 3 lanes (90 units)
        half_width = 45
        
        # Length of the field of view is proportional to the vehicle's speed
        length_front = 20  # Scale factor for front length
        length_back = 8   # Scale factor for back length
        
        # Calculate the corners of the field of view
        left_offset = direction_vector.rotate(90) * half_width
        right_offset = direction_vector.rotate(-90) * half_width
        front_offset = direction_vector * length_front
        back_offset = direction_vector * length_back
        
        front_left_quad = front_left + left_offset + front_offset
        front_right_quad = front_right + right_offset + front_offset
        back_left_quad = back_left + left_offset - back_offset
        back_right_quad = back_right + right_offset - back_offset
        
        return [front_left_quad, front_right_quad, back_right_quad, back_left_quad]
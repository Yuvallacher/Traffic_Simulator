import pygame.transform as transform
from pygame.surface import Surface
from pygame import mouse

class Button:
    def __init__(self, x : int, y : int, image : Surface, scale : float):
        width = image.get_width()
        height = image.get_height()
        self.image = transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
    
    def draw(self, surface : Surface) -> bool:
        action = False
        mousePosition = mouse.get_pos()
        
        if self.rect.collidepoint(mousePosition):
            if mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                action = True
            
        if not mouse.get_pressed()[0]:
            self.clicked = False
        
        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action
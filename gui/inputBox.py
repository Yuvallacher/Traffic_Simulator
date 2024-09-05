import pygame
from pygame import Rect

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

class InputBox:
    def __init__(self, x, y, w, h, font, defaultText='', text='', drawBorder=True):
        self.rect = Rect(x, y, w, h)
        self.color = BLACK
        self.text = text if text else defaultText
        self.default_text = defaultText
        self.active = False
        self.txt_surface = font.render(self.text, True, self.color)
        self.drawBorder = drawBorder

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
                if self.active and self.text == self.default_text:
                    self.text = ''
            else:
                self.active = False
            self.color = BLUE if self.active else BLACK

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = pygame.font.Font(None, 32).render(self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        if self.drawBorder:
            pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_text(self):
        return self.text if self.text else self.default_text

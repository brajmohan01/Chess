import pygame
from const import *

class Button:
    def __init__(self, x, y, w, h, text, color=(100, 100, 100), hover_color=(150, 150, 150)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.SysFont("monospace", 20, bold=True)

    def draw(self, surface):
        pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(pos) else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        lbl = self.font.render(self.text, 1, (255, 255, 255))
        surface.blit(lbl, lbl.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Checkbox:
    def __init__(self, x, y, size, text, checked=False):
        self.rect = pygame.Rect(x, y, size, size)
        self.text = text
        self.checked = checked
        self.font = pygame.font.SysFont("monospace", 18)

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 255), self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        if self.checked:
            pygame.draw.line(surface, (0, 0, 0), (self.rect.left + 2, self.rect.centery), (self.rect.centerx, self.rect.bottom - 2), 2)
            pygame.draw.line(surface, (0, 0, 0), (self.rect.centerx, self.rect.bottom - 2), (self.rect.right - 2, self.rect.top + 2), 2)
        lbl = self.font.render(self.text, 1, (200, 200, 200))
        surface.blit(lbl, (self.rect.right + 10, self.rect.y))

    def toggle(self, pos):
        if self.rect.collidepoint(pos):
            self.checked = not self.checked
            return True
        return False

class InputBox:
    def __init__(self, x, y, w, h, label="", text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = (100, 100, 100)
        self.color_active = (255, 255, 255)
        self.color = self.color_inactive
        self.text = text
        self.label = label
        self.font = pygame.font.SysFont("monospace", 18)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < 15: # Limit length
                        self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, (255, 255, 255))
        return None

    def draw(self, screen):
        # Draw label
        if self.label:
            lbl = self.font.render(self.label, True, (200, 200, 200))
            screen.blit(lbl, (self.rect.x, self.rect.y - 25))
        
        # Draw box
        pygame.draw.rect(screen, self.color, self.rect, 2)
        # Blit text
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 10))

class ConfirmationDialog:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = pygame.font.SysFont("monospace", 18, bold=True)
        self.btn_yes = Button(x + 20, y + h - 60, 100, 40, "YES", color=(50, 150, 50))
        self.btn_no = Button(x + w - 120, y + h - 60, 100, 40, "NO", color=(150, 50, 50))

    def draw(self, surface):
        pygame.draw.rect(surface, (50, 50, 50), self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        # Draw multi-line text
        lines = self.text.split('\n')
        for i, line in enumerate(lines):
            lbl = self.font.render(line, 1, (255, 255, 255))
            lbl_rect = lbl.get_rect(center=(self.rect.centerx, self.rect.y + 40 + i*25))
            surface.blit(lbl, lbl_rect)
            
        self.btn_yes.draw(surface)
        self.btn_no.draw(surface)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_yes.is_clicked(event.pos):
                return "YES"
            if self.btn_no.is_clicked(event.pos):
                return "NO"
        return None

import pygame

from src.view.components.component import Component
from src.view.constants import ui_constants as u


class InputBox(Component):
    def __init__(self, screen, pos, size, title, framerate, on_change, text=''):
        super().__init__(screen)
        self.pos = pos
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = (self.rect.topleft[0] - 250, self.rect.topleft[1] + 86)
        self.framerate = framerate
        self.color_inactive = u.COLOR_LIGHTGRAY,
        self.color_active = u.COLOR_GOLD,
        self.color = self.color_inactive
        self.text_color = u.COLOR_WHITE
        self.text = text
        self.title = title
        self.font = u.DEFAULT_FONT
        self.on_change = on_change
        self.title_font = u.CINZEL_30_BOLD
        self.active = False
        self.cursor_visible = True
        self.cursor_counter = 0
        self.cursor_position = len(text)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.cursor_counter = 0
            self.cursor_visible = True
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_position > 0:
                    self.text = self.text[:self.cursor_position-1] + self.text[self.cursor_position:]
                    self.on_change(self.text)
                    self.cursor_position -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_position < len(self.text):
                    self.text = self.text[:self.cursor_position] + self.text[self.cursor_position+1:]
                    self.on_change(self.text)
            elif event.key == pygame.K_LEFT:
                if self.cursor_position > 0:
                    self.cursor_position -= 1
            elif event.key == pygame.K_RIGHT:
                if self.cursor_position < len(self.text):
                    self.cursor_position += 1
            else:
                self.text = self.text[:self.cursor_position] + event.unicode + self.text[self.cursor_position:]
                self.on_change(self.text)
                self.cursor_position += 1

    def update_cursor(self):
        self.cursor_counter += 1
        if self.cursor_counter >= self.framerate:
            self.cursor_counter = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self):
        self.update_cursor()

        x, y = self.pos
        self.draw_text(self.title, x - self.rect.width // 2, y + 50, font=self.title_font, center=True)
        text_rect = self.draw_text(self.text, *self.rect.center, center=True)

        if self.active and self.cursor_visible:
            if self.text:
                cursor_x_pos = text_rect.x + self.font.size(self.text[:self.cursor_position])[0]
                cursor_y_pos = text_rect.y
            else:
                cursor_x_pos = self.rect.centerx
                cursor_y_pos = self.rect.centery - self.font.get_height() // 2

            cursor_height = self.font.get_height()
            pygame.draw.line(self.screen, self.text_color,
                             (cursor_x_pos, cursor_y_pos),
                             (cursor_x_pos, cursor_y_pos + cursor_height), 2)

        pygame.draw.rect(self.screen, self.color, self.rect, 2)

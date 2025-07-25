import pygame
from src.view.constants import ui_constants as u


class InputBox:
    def __init__(self, x, y, w, h, text='', font=None,
                 color_inactive=u.COLOR_GRAY,
                 color_active=u.COLOR_GOLD,
                 text_color=u.COLOR_LIGHTGRAY):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = color_inactive
        self.color_active = color_active
        self.color = self.color_inactive

        self.text_color = text_color

        # Font przekazany z zewnątrz lub domyślny
        self.font = font or pygame.font.SysFont(None, 32)

        self.text = text
        self.txt_surface = self.font.render(text, True, self.text_color)

        self.active = False
        self.cursor_visible = True
        self.cursor_counter = 0
        self.cursor_position = len(text)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Aktywacja inputa po kliknięciu
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return self.text  # można zwrócić tekst na Enter
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_position > 0:
                    self.text = self.text[:self.cursor_position-1] + self.text[self.cursor_position:]
                    self.cursor_position -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_position < len(self.text):
                    self.text = self.text[:self.cursor_position] + self.text[self.cursor_position+1:]
            elif event.key == pygame.K_LEFT:
                if self.cursor_position > 0:
                    self.cursor_position -= 1
            elif event.key == pygame.K_RIGHT:
                if self.cursor_position < len(self.text):
                    self.cursor_position += 1
            else:
                # Dodawanie znaku na pozycji kursora
                self.text = self.text[:self.cursor_position] + event.unicode + self.text[self.cursor_position:]
                self.cursor_position += 1

            self.txt_surface = self.font.render(self.text, True, self.text_color)

    def update(self):
        # Dopasowanie szerokości inputa do tekstu (min. 200)
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

        # Migający kursor
        self.cursor_counter += 1
        if self.cursor_counter >= 30:
            self.cursor_counter = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self, screen):
        # Rysuj tekst
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

        # Rysuj kursor jeśli aktywne i widoczne
        if self.active and self.cursor_visible:
            # Pozycja kursora w pikselach:
            cursor_x_pos = self.font.size(self.text[:self.cursor_position])[0] + self.rect.x + 5
            cursor_y_pos = self.rect.y + 5
            cursor_height = self.font.get_height()
            pygame.draw.line(screen, self.text_color, (cursor_x_pos, cursor_y_pos), (cursor_x_pos, cursor_y_pos + cursor_height), 2)

        # Rysuj obramowanie
        pygame.draw.rect(screen, self.color, self.rect, 2)

import pygame
from overrides import overrides

from src.view.constants import ui_constants as u
from src.view.scenes.scene import Scene
from src.view.components.button import Button


class TextScene(Scene):
    def __init__(self, screen, texts):
        super().__init__(screen)

        self.texts = texts

        button_width, button_height = u.BUTTON_SIZE_WIDE
        self.buttons = [
            Button("Powrót do Menu", ((self.screen_width - button_width) // 2, self.screen_height - button_height - 50),
                   u.BUTTON_SIZE_WIDE, self.button_menu, image_paths=self.theme_buttons_paths)
        ]

    @overrides
    def draw(self):
        super().draw()
        self.draw_overlay(0.60)

        lines = self.texts
        font = u.CINZEL_40
        line_height = font.get_height()
        spacing = 10

        total_height = len(lines) * line_height + (len(lines) - 1) * spacing
        start_y = (self.screen_height - total_height) // 2

        y_pos = start_y
        for line in lines:
            text_surface = font.render(line, True, u.COLOR_WHITE)
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_pos + line_height // 2))
            self.screen.blit(text_surface, text_rect)
            y_pos += line_height + spacing

        for button in self.buttons:
            button.draw(self.screen, pygame.mouse.get_pos())

    @overrides
    def handle_events(self, event):
        if self.locked:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons:
                if button.check_click(event.pos):
                    self.lock()
                    return button.on_click()

    def button_menu(self):
        self.lock()
        return {
            "type": "mode_change",
            "mode": "menu"
        }
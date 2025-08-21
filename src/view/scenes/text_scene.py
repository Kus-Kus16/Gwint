import pygame
from overrides import overrides

from src.view.constants import ui_constants as u
from src.view.scenes.scene import Scene
from src.view.components.button import Button


class TextScene(Scene):
    def __init__(self, screen, title, texts=None):
        super().__init__(screen)

        self.title = title
        self.texts = texts

        button_width, button_height = u.BUTTON_SIZE_WIDE
        self.buttons = [
            Button(l("scene.backtomenu"), ((self.screen_width - button_width) // 2, self.screen_height - button_height - 50),
                   u.BUTTON_SIZE_WIDE, self.button_menu, image_paths=self.theme_buttons_paths)
        ]

    @overrides
    def draw(self):
        super().draw()
        self.draw_overlay(0.60)

        title_pos = (self.screen_width // 2, 100) if self.texts else self.screen.get_rect().center
        self.draw_text(self.title, *title_pos, center=True, font=u.CINZEL_50_BOLD)

        for button in self.buttons:
            button.draw(self.screen, pygame.mouse.get_pos())

        if self.texts:
            self.draw_text_lines(self.texts, self.screen_width // 2, self.screen_height // 2)

    def draw_text_lines(self, lines, center_x, center_y, color=u.COLOR_WHITE, spacing=30):
        font = u.CINZEL_30_BOLD
        font_large = u.CINZEL_40

        line_height = font.get_height()
        block_height = len(lines) * (line_height + spacing) - spacing
        start_y = center_y - block_height // 2
        large = True

        for i, line in enumerate(lines):
            y = start_y + i * (line_height + spacing) + line_height // 2
            self.draw_text(line, center_x, y, color, font=font_large if large else font, center=True)
            large = not large

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
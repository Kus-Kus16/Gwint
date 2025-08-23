import pygame
from overrides import overrides

from src.view.constants import ui_constants as u
from src.view.scenes.scene import Scene
from src.view.components.button import Button


class TextScene(Scene):
    def __init__(self, screen, title, text=None):
        super().__init__(screen)

        self.title = title
        self.text = text

        button_width, button_height = u.BUTTON_SIZE_WIDE
        self.buttons = [
            Button(self.screen, "Return to Menu", ((self.screen_width - button_width) // 2, self.screen_height - button_height - 50),
                   u.BUTTON_SIZE_WIDE, self.button_menu, image_paths=self.theme_buttons_paths)
        ]

    @overrides
    def draw(self):
        super().draw()
        self.draw_overlay(0.75)

        title_pos = (self.screen_width // 2, 100) if self.text else self.screen.get_rect().center
        self.draw_text(self.title, *title_pos, center=True, font=u.CINZEL_50_BOLD)

        for button in self.buttons:
            button.draw(pygame.mouse.get_pos())

        if self.text:
            self.draw_text(self.text, self.screen_width // 2, self.screen_height // 2, center=True)

    @overrides
    def _draw_text_lines(self, lines, x, y, color=u.COLOR_WHITE, font0=u.CINZEL_30, font1=None, spacing=5,
                         centerx=False, centery=False, **kwargs):
        super()._draw_text_lines(lines, x, y, color, font0=u.CINZEL_40, font1=u.CINZEL_30_BOLD,
                                 centerx=centerx, centery=centery, spacing=20, **kwargs)

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
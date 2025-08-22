from abc import ABC
from src.view.constants import ui_constants as u


class Component(ABC):
    def __init__(self, screen):
        self.screen = screen

    def draw_text(self, text, x, y, color=u.COLOR_WHITE, font=u.CINZEL_30, center=False):
        text = str(text)
        lines = text.splitlines()
        if len(lines) > 1:
            self._draw_text_lines(lines, x, y, color, font, center=center)
            return

        text_surface = font.render(str(text), True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)

    def _draw_text_lines(self, lines, x, y, color=u.COLOR_WHITE, font0=u.CINZEL_30, font1=None, spacing=5, center=False):
        line_height = font0.get_height()
        block_height = len(lines) * (line_height + spacing) - spacing
        start_y = y - block_height // 2

        other_font = False
        for i, line in enumerate(lines):
            line_y = start_y + i * (line_height + spacing)
            current_font = font1 if (other_font and font1) else font0

            self.draw_text(line, x, line_y, color, font=current_font, center=center)
            other_font = not other_font
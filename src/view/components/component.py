from abc import ABC

from src.presenter.loader import Loader
from src.view.constants import ui_constants as u


class Component(ABC):
    def __init__(self, screen):
        self.screen = screen

    def draw_text(self, text, x, y, color=u.COLOR_WHITE, font=u.CINZEL_30, center=False,
                  centerx=False, centery=False, **kwargs):
        if text == "":
            return

        if center:
            centerx = centery = True

        text = str(text)
        lines = text.splitlines()
        if len(lines) > 1:
            self._draw_text_lines(lines, x, y, color, font, centerx=centerx, centery=centery)
            return

        text_surface = Loader.load_text(text, font, color, **kwargs)
        text_rect = text_surface.get_rect()

        if centerx:
            text_rect.centerx = x
        else:
            text_rect.x = x

        if centery:
            text_rect.centery = y
        else:
            text_rect.y = y

        self.screen.blit(text_surface, text_rect)
        return text_rect

    def _draw_text_lines(self, lines, x, y, color=u.COLOR_WHITE, font0=u.CINZEL_30, font1=None, spacing=5,
                         centerx=False, centery=False, **kwargs):
        if len(lines) > 2:
            spacing = 1

        line_height = font0.get_height()
        block_height = len(lines) * (line_height + spacing) - spacing

        if centery:
            start_y = y - block_height // 2
        else:
            start_y = y

        other_font = False
        for i, line in enumerate(lines):
            line_y = start_y + i * (line_height + spacing)
            current_font = font1 if (other_font and font1) else font0

            self.draw_text(line, x, line_y, color=color, font=current_font, centerx=centerx, centery=False, **kwargs)
            other_font = not other_font
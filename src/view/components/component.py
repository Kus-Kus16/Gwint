from abc import ABC
from src.view.constants import ui_constants as u


class Component(ABC):
    def __init__(self, font):
        self.font = font

    def draw_text(self, text, x, y, screen, color=u.COLOR_WHITE, font=None, center=False):
        if font is None:
            font = self.font

        text_surface = font.render(str(text), True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)

        screen.blit(text_surface, text_rect)
        return text_rect
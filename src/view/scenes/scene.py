from abc import ABC, abstractmethod

import pygame

from src.model.enums.card_type import CardType
from src.view.components.notification import Notification
from src.view import image_loader as loader, constants as c


class Scene(ABC):
    def __init__(self, screen, background_path=None, volume_slider=None):
        self.screen = screen
        self.framerate = c.FRAMERATE
        self.pos = (0, 0)
        self.size = screen.get_size()
        self.screen_width, self.screen_height = self.size
        self.rect = pygame.Rect(self.pos, self.size)
        self.background = loader.load_image(background_path if background_path is not None else c.BACKGROUND_PATH,
                                            (self.screen_width, self.screen_height))
        self.volume_slider = volume_slider
        self.temporary_drawable = []
        self.spacing_frames = 0
        self.locked = False

    @abstractmethod
    def draw(self):
        self.screen.blit(self.background, (0, 0))

    @abstractmethod
    def handle_events(self, event):
        return None

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def draw_temporary(self):
        if len(self.temporary_drawable) == 0:
            return

        drawable = self.temporary_drawable[0]

        if drawable.locking and drawable.starting_lock is None:
            drawable.starting_lock = self.locked
            self.lock()

        if self.spacing_frames > 0:
            self.spacing_frames -= 1
            return

        drawable.draw(self.screen)
        drawable.frames -= 1

        if drawable.frames == 0:
            self.temporary_drawable.pop(0)

            if drawable.locking:
                if drawable.starting_lock:
                    self.lock()
                else:
                    self.unlock()

    def draw_overlay(self, opacity):
        overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 255 * opacity))
        self.screen.blit(overlay, self.rect.topleft)

    def notification(self, name, frames, locking):
        pos = (0, self.screen_height // 2 - 60)
        size = (self.screen_width, 120)
        notification = Notification(pos, size, name, frames, locking)

        if len(self.temporary_drawable) == 0:
            self.spacing_frames = self.framerate // 2

        self.temporary_drawable.append(notification)

    def clear_temporary(self):
        self.temporary_drawable.clear()

    def draw_text(self, text, x, y, color=c.COLOR_WHITE, font=c.CINZEL_30, center=False):
        text_surface = font.render(str(text), True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)

    def reset_all(self):
        self.temporary_drawable = []
        self.spacing_frames = 0
        self.locked = False

    @classmethod
    def load_small_card_image(cls, faction, filename):
        path = f"resources/small/{faction}/{filename}.png"
        return loader.load_image(path, c.SMALL_CARD_SIZE)

    @classmethod
    def load_medium_card_image(cls, faction, filename):
        path = f"resources/large/{faction}/{filename}.png"
        return loader.load_image(path, c.MEDIUM_CARD_SIZE)

    @classmethod
    def load_large_card_image(cls, faction, filename):
        path = f"resources/large/{faction}/{filename}.png"
        return loader.load_image(path, c.LARGE_CARD_SIZE)

    def load_card_image(self, card, size):
        loaders = {
            "small": self.load_small_card_image,
            "medium": self.load_medium_card_image,
            "large": self.load_large_card_image,
        }

        return loaders[size](*self.get_card_paths(card, size))

    def get_card_paths(self, card, size):
        return None, None

    @classmethod
    def load_ico_image(cls, filename, size=None):
        path = f"resources/ico/{filename}.png"
        return loader.load_image(path, size)

    def draw_card(self, card, x, y, size, highlight=False):
        image = self.load_card_image(card, size)
        rect = image.get_rect(topleft=(x, y))
        self.screen.blit(image, rect)

        if highlight:
            radius = 5 if size == "small" else 10
            pygame.draw.rect(self.screen, c.COLOR_YELLOW, rect, width=4, border_radius=radius)

        if not card.is_card_type(CardType.UNIT) and not card.is_card_type(CardType.HERO):
            return rect

        if card.is_card_type(CardType.HERO):
            color = c.COLOR_WHITE
        elif card.power > card.base_power:
            color = c.COLOR_GREEN
        elif card.power < card.base_power:
            color = c.COLOR_RED
        else:
            color = c.COLOR_BLACK

        sizes = {
            "small": (c.MASON_20, c.MASON_30, (20, 20), (20, 20)),
            "medium": (c.MASON_30, c.MASON_40, (31, 34), (32, 34)),
            "large": (c.MASON_40, c.MASON_50, (43, 47), (45, 48))
        }

        font_small, font_large, offset_unit, offset_hero = sizes[size]
        font = font_large if card.power < 10 else font_small
        offset = offset_hero if card.is_card_type(CardType.HERO) else offset_unit

        self.draw_text(card.power, rect.x + offset[0], rect.y + offset[1], color=color, font=font, center=True)

        return rect

    def draw_label(self, text, x, y):
        overlay = pygame.Surface((60, 36), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))

        self.screen.blit(overlay, (x, y))
        self.draw_text(text, x + 30, y + 18, center=True)
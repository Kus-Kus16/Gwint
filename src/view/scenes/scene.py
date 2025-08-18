from abc import ABC, abstractmethod

import pygame

from src.model.enums.card_type import CardType
from src.view.components.notification import Notification
from src.view import loader as loader
from src.view.constants import ui_constants as u


class Scene(ABC):
    def __init__(self, screen, background_path=None, volume_slider=None):
        self.screen = screen
        self.framerate = u.FRAMERATE
        self.pos = (0, 0)
        self.size = screen.get_size()
        self.screen_width, self.screen_height = self.size
        self.rect = pygame.Rect(self.pos, self.size)
        self.background = loader.load_image(background_path if background_path is not None else u.BACKGROUND_PATH,
                                            (self.screen_width, self.screen_height))
        self.overlay = pygame.Surface(self.size, pygame.SRCALPHA)
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

    def handle_temporary(self, event):
        drawable = self.get_first_handleable_drawable()
        if drawable:
            return drawable.handle_events(event)

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def draw_temporary(self):
        if not self.temporary_drawable:
            return

        drawable = self.temporary_drawable[0]

        if drawable.locking and drawable.starting_lock is None:
            drawable.starting_lock = self.locked
            self.lock()

        if self.spacing_frames > 0:
            self.spacing_frames -= 1
            return

        drawable.draw()
        drawable.frames -= 1

        if drawable.frames == 0:
            self.pop_temporary()

    def draw_overlay(self, opacity):
        self.overlay.fill((0, 0, 0, 255 * opacity))
        self.screen.blit(self.overlay, self.rect.topleft)

    def notification(self, name, frames, locking):
        pos = (0, self.screen_height // 2 - 60)
        size = (self.screen_width, 120)
        notification = Notification(self.screen, pos, size, name, locking, frames)
        if not self.temporary_drawable:
            self.spacing_frames = self.framerate // 2

        for i, drawable in enumerate(self.temporary_drawable):
            if drawable.can_be_handled():
                self.temporary_drawable.insert(i, notification)
                return

        self.add_temporary(notification)

    def add_temporary(self, drawable):
        self.temporary_drawable.append(drawable)

    def pop_temporary(self):
        if not self.temporary_drawable:
            return

        drawable = self.temporary_drawable.pop(0)

        if not self.temporary_drawable:
            self.spacing_frames = 0

        if drawable.locking:
            if drawable.starting_lock:
                self.lock()
            else:
                self.unlock()

    def clear_temporary(self):
        self.temporary_drawable.clear()

    def get_first_handleable_drawable(self):
        for drawable in self.temporary_drawable:
            if drawable.can_be_handled():
                return drawable

    def draw_text(self, text, x, y, color=u.COLOR_WHITE, font=u.CINZEL_30, center=False):
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
        return loader.load_image(path, u.SMALL_CARD_SIZE)

    @classmethod
    def load_medium_card_image(cls, faction, filename):
        path = f"resources/large/{faction}/{filename}.png"
        return loader.load_image(path, u.MEDIUM_CARD_SIZE)

    @classmethod
    def load_large_card_image(cls, faction, filename):
        path = f"resources/large/{faction}/{filename}.png"
        return loader.load_image(path, u.LARGE_CARD_SIZE)

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
            pygame.draw.rect(self.screen, u.COLOR_YELLOW, rect, width=4, border_radius=radius)

        if not card.is_card_type(CardType.UNIT) and not card.is_card_type(CardType.HERO):
            return rect

        if card.is_card_type(CardType.HERO):
            color = u.COLOR_WHITE
        elif card.power > card.base_power:
            color = u.COLOR_GREEN
        elif card.power < card.base_power:
            color = u.COLOR_RED
        else:
            color = u.COLOR_BLACK

        sizes = {
            "small": (u.MASON_20, u.MASON_30, (20, 20), (20, 20)),
            "medium": (u.MASON_30, u.MASON_40, (31, 34), (32, 34)),
            "large": (u.MASON_40, u.MASON_50, (43, 47), (45, 48))
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

    def draw_icon(self, filename, size, x, y, center=False):
        image = self.load_ico_image(filename, size)
        rect = image.get_rect()

        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)

        self.screen.blit(image, rect)
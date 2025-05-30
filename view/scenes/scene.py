from abc import ABC, abstractmethod

import pygame

from view.components.notification import Notification
from view import constants as c, image_loader as loader

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

    def draw_overlay(self, transparency):
        overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 255 * transparency))
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

        return rect
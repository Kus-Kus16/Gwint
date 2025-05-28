import pygame
from abc import ABC, abstractmethod

from view.components.Notification import Notification
from view import Constants as C, ImageLoader


class Scene(ABC):
    def __init__(self, screen, background_path=C.BACKGROUND_PATH, volume_slider=None):
        self.screen = screen
        self.framerate = C.FRAMERATE
        self.screen_width, self.screen_height = screen.get_size()
        self.background = ImageLoader.load_image(background_path, (self.screen_width, self.screen_height))
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

    def notification(self, name, frames, locking):
        pos = (0, self.screen_height // 2 - 60)
        size = (self.screen_width, 120)
        notification = Notification(pos, size, name, frames, locking)

        if len(self.temporary_drawable) == 0:
            self.spacing_frames = self.framerate // 2

        self.temporary_drawable.append(notification)

    def clear_temporary(self):
        self.temporary_drawable.clear()

    def draw_text(self, text, x, y, color=C.COLOR_WHITE, font=C.CINZEL_30, center=False):
        text_surface = font.render(str(text), True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)
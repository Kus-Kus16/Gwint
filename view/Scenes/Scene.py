import pygame
from abc import ABC, abstractmethod

class Scene(ABC):
    def __init__(self, screen, font, background_path):
        self.screen = screen
        self.font = font
        self.screen_width, self.screen_height = screen.get_size()
        self.background = pygame.image.load(background_path)
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))

    @abstractmethod
    def draw(self):
        self.screen.blit(self.background, (0, 0))

    @abstractmethod
    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            return "action"
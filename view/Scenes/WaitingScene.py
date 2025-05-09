import pygame
from overrides import overrides

from view.Scenes.Scene import Scene
from view.components.Button import Button


class WaitingScene(Scene):
    def __init__(self, screen, framerate, font):
        super().__init__(screen, framerate, font, "resources/menu.png")

        self.back_button = Button("Powrót do Menu", (self.screen_width // 2 - 200, self.screen_height - 150),
          (400, 100), { "type": "mode_change", "mode": "menu" }, self.font)

        self.background = pygame.image.load("resources/menu.png").convert()
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))

        self.darken = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.darken.fill((0, 0, 0, 150))

    @overrides
    def draw(self):
        super().draw()
        self.screen.blit(self.darken, (0, 0))

        text = self.font.render("Oczekiwanie na przeciwnika", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(text, text_rect)

        self.back_button.draw(self.screen, pygame.mouse.get_pos())


    @overrides
    def handle_events(self, event):
        if self.locked:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.check_click(event.pos):
                self.lock()
                return self.back_button.action

import pygame
from overrides import overrides

from view import Constants as C
from view.Scenes.Scene import Scene
from view.components.Button import Button


class CreditsScene(Scene):
    def __init__(self, screen, framerate, font):
        super().__init__(screen, framerate, font, "resources/menu.png")

        button_width, button_height = C.BUTTON_SIZE_WIDE
        self.back_button = Button("Powrót do Menu",((self.screen_width - button_width) // 2, self.screen_height - button_height - 50),
          C.BUTTON_SIZE_WIDE, { "type": "mode_change", "mode": "menu" }, self.font)

        self.darken = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.darken.fill((0, 0, 0, 150))

    @overrides
    def draw(self):
        super().draw()
        self.screen.blit(self.darken, (0, 0))

        credits_text = [
            "Autorzy:",
            "Krzysztof Pieczka",
            "Maciej Kus"
        ]

        y_pos = self.screen_height // 2 - 80

        for line in credits_text:
            text = self.font.render(line, True, C.COLOR_WHITE)
            text_rect = text.get_rect(center=(self.screen_width // 2, y_pos))
            self.screen.blit(text, text_rect)
            y_pos += 50

        self.back_button.draw(self.screen, pygame.mouse.get_pos())

    @overrides
    def handle_events(self, event):
        if self.locked:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.check_click(event.pos):
                self.lock()
                return self.back_button.action
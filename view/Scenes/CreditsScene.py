import pygame
from overrides import overrides

from view.Scenes.Scene import Scene
from view.components.Button import Button


class CreditsScene(Scene):
    def __init__(self, screen, font):
        super().__init__(screen, font, "resources/menu.png")

        self.back_button = Button("Powrót do Menu",(self.screen_width // 2 - 200, self.screen_height - 150),
          (400, 100), { "type": "mode_change", "mode": "menu" }, self.font)

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
            text = self.font.render(line, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen_width // 2, y_pos))
            self.screen.blit(text, text_rect)
            y_pos += 50

        self.back_button.draw(self.screen)
        self.back_button.on_hover(pygame.mouse.get_pos())

    @overrides
    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.check_click(event.pos):
                return self.back_button.action
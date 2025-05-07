import pygame
from overrides import overrides

from view import ImageLoader
from view.Scenes.Scene import Scene
from view.components.Button import Button


class CarouselScene(Scene):
    def __init__(self, screen, framerate, font, cards, draw_card):
        super().__init__(screen, framerate, font, "resources/board.jpg")
        self.cards = cards
        self.draw_card = draw_card
        self.selected_index = 0
        self.buttons = [
            Button("Wybierz", (self.screen_width // 2, self.screen_height - 100),
                   (120, 50), {"type": "select"}, font) ]

    @overrides
    def draw(self):
        super().draw()

        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        for i, card in enumerate(self.cards):
            offset = (i - self.selected_index) * 140
            self.draw_card(card, center_x + offset, center_y, "large")

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.draw(self.screen, mouse_pos)

    @overrides
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = min(len(self.cards) - 1, self.selected_index + 1)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn.check_click(event.pos):
                    card = self.cards[self.selected_index]
                    self.cards.remove(card)
                    return card
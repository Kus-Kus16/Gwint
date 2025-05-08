import pygame
from overrides import overrides

from view import ImageLoader
from view.Scenes.Scene import Scene
from view.components.Button import Button


class CarouselScene(Scene):
    def __init__(self, screen, framerate, font, cards, draw_card):
        super().__init__(screen, framerate, font, "resources/board.jpg")
        self.cards = list(cards)
        self.draw_card = draw_card
        self.selected_index = 0
        self.buttons = [
            Button("Wybierz", (self.screen_width // 2 - 150, self.screen_height - 200),
                   (300, 100), {"type": "select"}, font) ]

    @overrides
    def draw(self):
        # 668x1164
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        visible_cards = 3
        half_visible = visible_cards // 2
        card_width, card_height = 668//2, 1164//2

        for i in range(-half_visible, half_visible + 1):
            card_index = self.selected_index + i

            if 0 <= card_index < len(self.cards):
                card = self.cards[card_index]
                offset_x = i * (card_width + 140)
                top_left_x = center_x + offset_x - card_width // 2
                top_left_y = center_y - card_height // 2
                self.draw_card(card, top_left_x, top_left_y, "large")

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.draw(self.screen, mouse_pos)

    @overrides
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_index = max(self.selected_index - 1, 0)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = min(self.selected_index + 1, len(self.cards) - 1)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            center_x = self.screen_width // 2
            center_y = self.screen_height // 2
            card_width, card_height = 668 // 2, 1164 // 2
            offset = card_width + 140

            for i in range(-1, 2):
                card_x = center_x + i * offset - card_width // 2
                card_y = center_y - card_height // 2
                if card_x <= mouse_x <= card_x + card_width and card_y <= mouse_y <= card_y + card_height:
                    self.selected_index = (self.selected_index + i) % len(self.cards)
                    return
            for btn in self.buttons:
                if btn.check_click(event.pos):
                    card = self.cards[self.selected_index]
                    self.cards.remove(card)
                    self.lock()
                    return card

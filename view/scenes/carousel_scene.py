import pygame
from overrides import overrides

from model.enums.ability_type import AbilityType
from view import constants as c
from view.scenes.scene import Scene
from view.components.button import Button


class CarouselScene(Scene):
    def __init__(self, screen, draw_card, cards, choose_count, cancelable, label=True, font=None):
        super().__init__(screen)
        self.font = font if font is not None else c.DEFAULT_FONT
        self.cards = list(cards)
        self.draw_card = draw_card
        self.selected_index = 0
        self.choose_count = choose_count
        self.choosable = choose_count != 0
        self.cancellable = cancelable
        self.label = label
        self.buttons = []

        button_width, button_height = c.BUTTON_SIZE
        button_margin = 150
        button_y = self.screen_height - 200

        button_data = []
        if self.choosable:
            button_data.append(("Wybierz", {"type": "select"}))
        if self.cancellable:
            button_data.append(("Zamknij", {"type": "cancel"}))

        total_width = len(button_data) * button_width + (len(button_data) - 1) * button_margin
        start_x = self.screen_width // 2 - total_width // 2

        for i, (label, action) in enumerate(button_data):
            x = start_x + i * (button_width + button_margin)
            self.buttons.append(Button(label, (x, button_y), c.BUTTON_SIZE, action))

    @overrides
    def draw(self):
        self.draw_overlay(0.25)

        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        if self.label:
            height = c.BUTTON_SIZE[1]
            overlay = pygame.Surface((self.screen_width, height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 205))
            self.screen.blit(overlay, (0, 100))

            text = self.font.render(f"Wybierz do {self.choose_count} kart, które chcesz wymienić.", True, c.COLOR_GOLD)
            text_rect = text.get_rect()
            text_rect.center = (self.screen_width // 2, 100 + height // 2)
            self.screen.blit(text, text_rect)

        visible_cards = 3
        half_visible = visible_cards // 2
        card_width, card_height = c.LARGE_CARD_SIZE

        for i in range(-half_visible, half_visible + 1):
            card_index = self.selected_index + i

            if 0 <= card_index < len(self.cards):
                card = self.cards[card_index]
                offset_x = i * (card_width + 140)
                top_left_x = center_x + offset_x - card_width // 2
                top_left_y = center_y - card_height // 2
                self.draw_card(card, top_left_x, top_left_y, "large", highlight=i == 0)

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
            card_width, card_height = c.LARGE_CARD_SIZE
            offset = card_width + 140

            for i in range(-1, 2):
                card_x = center_x + i * offset - card_width // 2
                card_y = center_y - card_height // 2
                if card_x <= mouse_x <= card_x + card_width and card_y <= mouse_y <= card_y + card_height:
                    self.selected_index = max(0, min(len(self.cards) - 1, self.selected_index + i))
                    return

            return self.handle_button_events(event)

    def handle_button_events(self, event):
        for btn in self.buttons:
            if btn.check_click(event.pos):
                if btn.action["type"] == "cancel":
                    return {
                        "type": "carousel",
                        "card_id": None,
                        "end": True
                    }

                card = self.cards[self.selected_index]
                self.cards.remove(card)
                self.choose_count -= 1
                self.lock()

                end = False
                if self.choose_count == 0 or len(self.cards) == 0:
                    end = True
                if self.choose_count < 0 and not card.is_ability_type(AbilityType.CHOOSING):
                    end = True

                return {
                    "type": "carousel",
                    "card_id": card.id if hasattr(card, "id") else card["id"],
                    "end": end
                }

    def set_cards(self, cards):
        self.cards = cards

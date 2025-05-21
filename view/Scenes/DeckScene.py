import pygame
from overrides import overrides

from view import Constants as C, ImageLoader
from view.Scenes.Scene import Scene
from view.components.Button import Button

CARD_MARGIN = 10
VISIBLE_CARDS = 4

ROWS = 2
COLS = 2
CARDS_PER_PAGE = ROWS * COLS

def load_small_image(card):
    path = f"resources/small/{card['faction']}/{card['filename']}.png"
    return ImageLoader.load_image(path, C.SMALL_CARD_SIZE)

def load_large_image(card):
    faction = card['owner']['faction'] if card['faction'] == "Neutralne" and 'owner' in card else card['faction']
    path = f"resources/large/{faction}/{card['filename']}.png"
    return ImageLoader.load_image(path, C.LARGE_CARD_SIZE)

def load_card_image(card, size):
    return load_small_image(card) if size == "small" else load_large_image(card)

class DeckScene(Scene):
    def __init__(self, screen, all_cards, current_decks):
        super().__init__(screen, "resources/menu.png")
        self.all_cards = all_cards
        self.current_decks = current_decks
        self.scroll_offset = 0

        self.scroll_offset_all = 0
        self.scroll_offset_deck = 0

        self.filtered_cards = [card for card in self.all_cards if card["faction"] == "Królestwa Północy"]

        self.factions = ["Królestwa Północy", "Cesarstwo Nilfgaardu", "Potwory", "Scoia'tael", "Skellige"]  # Przykład frakcji
        self.current_faction_index = 0
        self.filtered_cards = None
        self.update_filtered_cards()

        button_width, button_height = C.BUTTON_SIZE_WIDE
        self.back_button = Button("Powrót do Menu",
                                  ((self.screen_width - button_width) // 2, self.screen_height - button_height - 50),
                                  C.BUTTON_SIZE_WIDE,
                                  { "type": "mode_change", "mode": "menu" })

        self.prev_faction_button = Button("<", (50, 50), (50, 50),
                                          {"type": "change_faction", "direction": -1})
        self.next_faction_button = Button(">", (self.screen_width - 100, 50), (50, 50),
                                          {"type": "change_faction", "direction": 1})

        self.darken = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.darken.fill((0, 0, 0, 150))

    @overrides
    def draw(self):
        super().draw()
        self.screen.blit(self.darken, (0, 0))

        self.prev_faction_button.draw(self.screen, pygame.mouse.get_pos())
        self.next_faction_button.draw(self.screen, pygame.mouse.get_pos())

        font = pygame.font.SysFont(None, 36)
        faction_name = self.factions[self.current_faction_index]
        text_surface = font.render(f"Frakcja: {faction_name}", True, (255, 255, 255))
        self.screen.blit(text_surface, (self.screen_width // 2 - text_surface.get_width() // 2, 60))

        visible_cards = self.filtered_cards[self.scroll_offset_all:self.scroll_offset_all + CARDS_PER_PAGE]
        for idx, card in enumerate(visible_cards):
            image = load_card_image(card, "large")
            row = idx // COLS
            col = idx % COLS
            x = 50 + col * (C.LARGE_CARD_SIZE[0] + CARD_MARGIN)
            y = 100 + row * (C.LARGE_CARD_SIZE[1] + CARD_MARGIN)
            self.screen.blit(image, (x, y))

        deck_cards = self.get_deck_cards(0)

        expanded_deck_cards = []
        for entry in deck_cards:
            expanded_deck_cards.extend([entry["card"]] * entry["count"])

        visible_deck_cards = expanded_deck_cards[self.scroll_offset_deck:self.scroll_offset_deck + CARDS_PER_PAGE]

        for idx, card in enumerate(visible_deck_cards):
            image = load_card_image(card, "large")
            row = idx // COLS
            col = idx % COLS

            total_width = COLS * C.LARGE_CARD_SIZE[0] + (COLS - 1) * CARD_MARGIN
            x_start = self.screen_width - total_width - 50
            x = x_start + col * (C.LARGE_CARD_SIZE[0] + CARD_MARGIN)
            y = 100 + row * (C.LARGE_CARD_SIZE[1] + CARD_MARGIN)
            self.screen.blit(image, (x, y))

        self.back_button.draw(self.screen, pygame.mouse.get_pos())

    @overrides
    def handle_events(self, event):
        if self.locked:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.back_button.check_click(event.pos):
                    self.lock()
                    return self.back_button.action

                if self.prev_faction_button.check_click(event.pos):
                    self.current_faction_index = (self.current_faction_index - 1) % len(self.factions)
                    self.update_filtered_cards()

                if self.next_faction_button.check_click(event.pos):
                    self.current_faction_index = (self.current_faction_index + 1) % len(self.factions)
                    self.update_filtered_cards()

            elif event.button in (4, 5):  # Scroll
                mouse_x, _ = pygame.mouse.get_pos()
                is_left_side = mouse_x < self.screen_width // 2

                if is_left_side:
                    if event.button == 4:  # Scroll up
                        self.scroll_offset_all = max(0, self.scroll_offset_all - COLS)
                    elif event.button == 5:  # Scroll down
                        max_scroll = max(0, len(self.filtered_cards) - CARDS_PER_PAGE)
                        self.scroll_offset_all = min(max_scroll, self.scroll_offset_all + COLS)
                else:
                    deck_cards = self.get_deck_cards(0)
                    if event.button == 4: # Scroll up
                        self.scroll_offset_deck = max(0, self.scroll_offset_deck - COLS)
                    elif event.button == 5:
                        max_scroll = max(0, len(deck_cards) - CARDS_PER_PAGE)
                        self.scroll_offset_deck = min(max_scroll, self.scroll_offset_deck + COLS)

    def get_deck_cards(self, index):
        deck = self.current_decks[index]
        return [
            {
                "card": next(card for card in self.all_cards if card["id"] == entry["id"]),
                "count": entry["count"]
            }
            for entry in deck
        ]

    def update_filtered_cards(self):
        faction = self.factions[self.current_faction_index]
        self.filtered_cards = [card for card in self.all_cards if card["faction"] == faction]
        self.scroll_offset_all = 0
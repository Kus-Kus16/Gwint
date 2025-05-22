import json

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
        self.mode = "menu"
        self.all_cards = all_cards
        self.current_decks = current_decks
        self.scroll_offset = 0

        self.scroll_offset_all = 0
        self.scroll_offset_deck = 0

        self.factions = ["Królestwa Północy", "Cesarstwo Nilfgaardu", "Potwory", "Scoia'tael", "Skellige"]
        self.current_faction_index = 0
        self.current_deck_index = 0

        self.filtered_cards = None
        self.update_filtered_cards()

        # Click rects
        self.left_card_rects = []
        self.right_card_rects = []

        button_width, button_height = C.BUTTON_SIZE_WIDE
        self.back_button = Button("Powrót do Menu",
                                  ((self.screen_width - button_width) // 2, self.screen_height - button_height - 50),
                                  C.BUTTON_SIZE_WIDE,
                                  {"type": "mode_change", "mode": "menu"})

        self.start_button = Button("Rozpocznij grę",
                                  ((self.screen_width - button_width) // 2, self.screen_height - button_height - 50),
                                  C.BUTTON_SIZE_WIDE,
                                  {"type": "mode_change", "mode": "choose_deck", "deck_id": self.current_deck_index})

        self.prev_faction_button = None
        self.next_faction_button = None
        self.update_faction_buttons()

        self.darken = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.darken.fill((0, 0, 0, 200))

    def set_mode(self, mode):
        self.mode = mode

    def update_faction_buttons(self):
        prev_index = (self.current_faction_index - 1) % len(self.factions)
        next_index = (self.current_faction_index + 1) % len(self.factions)

        prev_name = self.factions[prev_index]
        next_name = self.factions[next_index]

        self.prev_faction_button = Button(f"< {prev_name}", (50, 50), (400, 50),
                                          {"type": "change_faction", "direction": -1})
        self.next_faction_button = Button(f"{next_name} >", (self.screen_width - 450, 50), (450, 50),
                                          {"type": "change_faction", "direction": 1})

    @overrides
    def draw(self):
        super().draw()
        self.screen.blit(self.darken, (0, 0))

        self.prev_faction_button.draw(self.screen, pygame.mouse.get_pos())
        self.next_faction_button.draw(self.screen, pygame.mouse.get_pos())

        font = C.CINZEL_40
        faction_name = self.factions[self.current_faction_index]
        text_surface = font.render(f"Frakcja: {faction_name}", True, C.COLOR_GOLD)
        self.screen.blit(text_surface, (self.screen_width // 2 - text_surface.get_width() // 2, 60))

        self.left_card_rects = []
        visible_cards = self.filtered_cards[self.scroll_offset_all:self.scroll_offset_all + CARDS_PER_PAGE]
        for idx, card in enumerate(visible_cards):
            image = load_card_image(card, "large")
            row = idx // COLS
            col = idx % COLS
            x = 50 + col * (C.LARGE_CARD_SIZE[0] + CARD_MARGIN)
            y = 100 + row * (C.LARGE_CARD_SIZE[1] + CARD_MARGIN)
            self.screen.blit(image, (x, y))
            self.left_card_rects.append((pygame.Rect(x, y, *C.LARGE_CARD_SIZE), card))

        deck_cards = self.get_deck_cards(self.current_deck_index)
        expanded_deck_cards = []
        for entry in deck_cards:
            expanded_deck_cards.extend([entry["card"]] * entry["count"])

        self.right_card_rects = []
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
            self.right_card_rects.append((pygame.Rect(x, y, *C.LARGE_CARD_SIZE), card))

        total_count, hero_count, special_count, total_strength = self.calculate_deck_stats()

        stats_font = C.CINZEL_40
        lines = [
            "Karty",
            f"{total_count}",
            "Bohaterowie",
            f"{hero_count}",
            "Specjalne",
            f"{special_count}",
            "Siła",
            f"{total_strength}"
        ]
        line_height = stats_font.get_height()
        start_y = 300
        for i, line in enumerate(lines):
            stats_surface = stats_font.render(line, True, C.COLOR_GOLD)
            stats_x = self.screen_width // 2 - stats_surface.get_width() // 2
            stats_y = start_y + i * (line_height + 10)
            self.screen.blit(stats_surface, (stats_x, stats_y))

        if self.mode == "menu":
            self.back_button.draw(self.screen, pygame.mouse.get_pos())
        else:
            self.start_button.draw(self.screen, pygame.mouse.get_pos())

    @overrides
    def handle_events(self, event):
        if self.locked:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.mode != "menu":
                    if self.start_button.check_click(event.pos):
                        self.lock()
                        with open("./data/yourdecks.json", "w", encoding="utf-8") as f:
                            json.dump(self.current_decks, f, ensure_ascii=False, indent=4)
                        self.start_button.action["deck_id"] = self.current_deck_index
                        return self.start_button.action
                else:
                    if self.back_button.check_click(event.pos):
                        self.lock()
                        with open("./data/yourdecks.json", "w", encoding="utf-8") as f:
                            json.dump(self.current_decks, f, ensure_ascii=False, indent=4)
                        return self.back_button.action

                # Prev faction button
                if self.prev_faction_button.check_click(event.pos):
                    self.current_faction_index = (self.current_faction_index - 1) % len(self.factions)
                    self.current_deck_index = self.current_faction_index
                    self.update_filtered_cards()
                    self.update_faction_buttons()
                    self.scroll_offset_deck = 0

                # Next faction button
                if self.next_faction_button.check_click(event.pos):
                    self.current_faction_index = (self.current_faction_index + 1) % len(self.factions)
                    self.current_deck_index = self.current_faction_index
                    self.update_filtered_cards()
                    self.update_faction_buttons()
                    self.scroll_offset_deck = 0

                # Add card to deck
                for rect, card in self.left_card_rects:
                    if rect.collidepoint(event.pos):
                        self.add_card_to_deck(card)
                        break

                # Remove card from deck
                for rect, card in self.right_card_rects:
                    if rect.collidepoint(event.pos):
                        self.remove_card_from_deck(card)
                        break

            # Scroll up/down
            elif event.button in (4, 5):
                mouse_x, _ = pygame.mouse.get_pos()
                is_left_side = mouse_x < self.screen_width // 2

                if is_left_side:
                    if event.button == 4: # Scroll up
                        self.scroll_offset_all = max(0, self.scroll_offset_all - COLS)
                    elif event.button == 5: # Scroll down
                        max_scroll = max(0, len(self.filtered_cards) - CARDS_PER_PAGE)
                        self.scroll_offset_all = min(max_scroll, self.scroll_offset_all + COLS)
                else:
                    deck_cards = self.get_deck_cards(self.current_deck_index)
                    expanded_deck_cards = []
                    for entry in deck_cards:
                        expanded_deck_cards.extend([entry["card"]] * entry["count"])

                    if event.button == 4:  # Scroll up
                        self.scroll_offset_deck = max(0, self.scroll_offset_deck - COLS)
                    elif event.button == 5:  # Scroll down
                        max_scroll = max(0, len(expanded_deck_cards) - CARDS_PER_PAGE)
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

    def calculate_deck_stats(self):
        deck_cards = self.get_deck_cards(self.current_deck_index)
        total_count = 0
        hero_count = 0
        special_count = 0
        total_strength = 0

        for entry in deck_cards:
            card = entry["card"]
            count = entry["count"]
            total_count += count
            if "hero" in card.get('abilities'):
                hero_count += count
            elif card.get('abilities'):
                special_count += count

            total_strength += card.get('power', 0) * count

        return total_count, hero_count, special_count, total_strength

    def add_card_to_deck(self, card):
        deck = self.current_decks[self.current_deck_index]
        for entry in deck:
            if entry["id"] == card["id"]:
                entry["count"] += 1
                break
        else:
            deck.append({"id": card["id"], "count": 1})

    def remove_card_from_deck(self, card):
        deck = self.current_decks[self.current_deck_index]
        for entry in deck:
            if entry["id"] == card["id"]:
                entry["count"] -= 1
                if entry["count"] <= 0:
                    deck.remove(entry)
                break
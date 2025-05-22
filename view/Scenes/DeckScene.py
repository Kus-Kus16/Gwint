import json

import pygame
from overrides import overrides

from view import Constants as C, ImageLoader
from view.Constants import BUTTON_SIZE_WIDE
from view.Scenes.CarouselScene import CarouselScene
from view.Scenes.GameScene import GameScene
from view.Scenes.Scene import Scene
from view.components.Button import Button

CARD_MARGIN = 20
VISIBLE_CARDS = 6

ROWS = 2
COLS = 3
CARDS_PER_PAGE = ROWS * COLS

def load_small_image(card):
    path = f"resources/small/{card['faction']}/{card['filename']}.png"
    return ImageLoader.load_image(path, C.SMALL_CARD_SIZE)

def load_large_image(card, faction):
    path = f"resources/large/{faction}/{card['filename']}.png"
    return ImageLoader.load_image(path, C.MEDIUM_CARD_SIZE)

def load_card_image(card, size, faction):
    return load_small_image(card) if size == "small" else load_large_image(card, faction)

class DeckScene(Scene):
    def __init__(self, screen, all_cards, current_decks):
        super().__init__(screen, "resources/menu.png")
        self.mode = "menu"
        self.all_cards = all_cards
        self.current_decks = current_decks
        self.scroll_offset = 0

        self.scroll_offset_all = 0
        self.scroll_offset_deck = 0

        self.current_faction_index = 0
        self.current_deck_index = 0

        # Commander
        with open("./data/factions.json", "r", encoding="utf-8") as f:
            self.factions_data = json.load(f)
        self.factions = [f["name"] for f in self.factions_data]
        self.current_commander_id = self.current_decks[self.current_deck_index].get("commander_id", None)
        self.commander_rect= None

        self.carousel_scene = None
        self.show_carousel = False

        self.filtered_cards = None
        self.update_filtered_cards()

        # Click rects
        self.left_card_rects = []
        self.right_card_rects = []

        button_width, button_height = C.BUTTON_SIZE_WIDE
        self.back_button = Button("Powrót do Menu",
                                  ((self.screen_width - button_width) // 2, self.screen_height - button_height - 30),
                                  C.BUTTON_SIZE_WIDE,
                                  {"type": "mode_change", "mode": "menu"})

        self.start_button = Button("Rozpocznij grę",
                                  ((self.screen_width - button_width) // 2, self.screen_height - button_height - 30 - button_height - 30),
                                  C.BUTTON_SIZE_WIDE,
                                  {"type": "mode_change", "mode": "choose_deck", "deck_id": self.current_deck_index, "commander_id": self.current_commander_id})

        self.prev_faction_button = None
        self.next_faction_button = None
        self.update_faction_buttons()

        self.darken = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.darken.fill((0, 0, 0, 230))

    def set_mode(self, mode):
        self.mode = mode

    def update_faction_buttons(self):
        prev_index = (self.current_faction_index - 1) % len(self.factions)
        next_index = (self.current_faction_index + 1) % len(self.factions)

        prev_name = self.factions[prev_index]
        next_name = self.factions[next_index]

        self.prev_faction_button = Button(f"< {prev_name}", (50, 50), BUTTON_SIZE_WIDE,
                                          {"type": "change_faction", "direction": -1})
        self.next_faction_button = Button(f"{next_name} >", (self.screen_width - 450, 50), BUTTON_SIZE_WIDE,
                                          {"type": "change_faction", "direction": 1})

    @overrides
    def draw(self):
        if self.show_carousel:
            self.carousel_scene.draw()
        else:
            super().draw()
            self.screen.blit(self.darken, (0, 0))

            self.draw_texts()

            self.show_all_available_cards()

            self.show_deck_cards()

            self.show_deck_stats()

            self.draw_buttons()

            # Draw the commander
            commander = self.get_commander_by_id(self.current_commander_id)
            if commander:
                commander_image = load_card_image(commander, "large", self.factions[self.current_faction_index])
                self.screen.blit(commander_image, (self.screen_width // 2 - C.MEDIUM_CARD_SIZE[0] // 2, 170))
                commander_pos = (self.screen_width // 2 - C.MEDIUM_CARD_SIZE[0] // 2, 170)
                self.commander_rect = pygame.Rect(commander_pos, C.MEDIUM_CARD_SIZE)

    def draw_buttons(self):
        self.prev_faction_button.draw(self.screen, pygame.mouse.get_pos())
        self.next_faction_button.draw(self.screen, pygame.mouse.get_pos())
        self.back_button.draw(self.screen, pygame.mouse.get_pos())
        if self.mode == "start" and self.can_start_game():
            self.start_button.draw(self.screen, pygame.mouse.get_pos())

    def draw_texts(self):
        # Titles
        font = C.CINZEL_30_BOLD
        text_surface = font.render(f"Kolekcja kart", True, C.COLOR_GOLD)
        self.screen.blit(text_surface, (50, 180))
        text_surface = font.render(f"Karty w talii", True, C.COLOR_GOLD)
        self.screen.blit(text_surface, (self.screen_width - text_surface.get_width() - 50, 180))
        # Faction name
        font = C.CINZEL_50_BOLD
        faction_name = self.factions[self.current_faction_index]
        text_surface = font.render(f"Frakcja: {faction_name}{self.current_commander_id}", True, C.COLOR_GOLD)
        self.screen.blit(text_surface, (self.screen_width // 2 - text_surface.get_width() // 2, 50))
        # Commander
        commander = self.get_commander_by_id(self.current_commander_id)
        if commander:
            font = C.CINZEL_30_BOLD
            text_surface = font.render("Dowódca", True, C.COLOR_GOLD)
            self.screen.blit(text_surface, (self.screen_width // 2 - text_surface.get_width() // 2, 130))

    def show_deck_stats(self):
        total_count, hero_count, special_count, total_strength = self.calculate_deck_stats()
        stats_font = C.CINZEL_25_BOLD
        lines = [
            "Karty (min. 22)",
            f"{total_count}",
            "Bohaterowie",
            f"{hero_count}",
            "Specjalne",
            f"{special_count}/10",
            "Siła",
            f"{total_strength}"
        ]
        line_height = stats_font.get_height()
        start_y = 550
        for i, line in enumerate(lines):
            color = C.COLOR_GOLD
            if i == 1:  # Total count
                color = C.COLOR_GREEN if total_count >= 22 else C.COLOR_RED
            elif i == 5:  # Special count
                color = C.COLOR_GREEN if special_count <= 10 else C.COLOR_RED

            stats_surface = stats_font.render(line, True, color)
            stats_x = self.screen_width // 2 - stats_surface.get_width() // 2
            stats_y = start_y + i * (line_height + 3)
            self.screen.blit(stats_surface, (stats_x, stats_y))

    def show_deck_cards(self):
        deck_cards = self.get_deck_cards(self.current_deck_index)
        expanded_deck_cards = []
        for entry in deck_cards:
            expanded_deck_cards.extend([entry["card"]] * entry["count"])
        self.right_card_rects = []
        visible_deck_cards = expanded_deck_cards[self.scroll_offset_deck:self.scroll_offset_deck + CARDS_PER_PAGE]
        for idx, card in enumerate(visible_deck_cards):
            image = load_card_image(card, "large", self.factions[self.current_faction_index])
            row = idx // COLS
            col = idx % COLS
            total_width = COLS * C.MEDIUM_CARD_SIZE[0] + (COLS - 1) * CARD_MARGIN
            x_start = self.screen_width - total_width - 70
            x = x_start + col * (C.MEDIUM_CARD_SIZE[0] + CARD_MARGIN)
            y = 270 + row * (C.MEDIUM_CARD_SIZE[1] + CARD_MARGIN)
            self.screen.blit(image, (x, y))
            self.right_card_rects.append((pygame.Rect(x, y, *C.MEDIUM_CARD_SIZE), card))

    def show_all_available_cards(self):
        self.left_card_rects = []
        visible_cards = self.filtered_cards[self.scroll_offset_all:self.scroll_offset_all + CARDS_PER_PAGE]
        for idx, card in enumerate(visible_cards):
            image = load_card_image(card, "large", self.factions[self.current_faction_index])
            row = idx // COLS
            col = idx % COLS
            x = 70 + col * (C.MEDIUM_CARD_SIZE[0] + CARD_MARGIN)
            y = 270 + row * (C.MEDIUM_CARD_SIZE[1] + CARD_MARGIN)
            self.screen.blit(image, (x, y))
            self.left_card_rects.append((pygame.Rect(x, y, *C.MEDIUM_CARD_SIZE), card))

    @overrides
    def handle_events(self, event):
        if self.show_carousel:
            result = self.carousel_scene.handle_events(event)
            if result is not None:
                self.set_commander(result)
                self.close_carousel()
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Back button
                if self.back_button.check_click(event.pos):
                    self.lock()
                    with open("./data/yourdecks.json", "w", encoding="utf-8") as f:
                        json.dump(self.current_decks, f, ensure_ascii=False, indent=4)
                    return self.back_button.action

                # Start button
                if self.mode == "start" and self.can_start_game():
                    if self.start_button.check_click(event.pos):
                        self.lock()
                        with open("./data/yourdecks.json", "w", encoding="utf-8") as f:
                            json.dump(self.current_decks, f, ensure_ascii=False, indent=4)
                        self.start_button.action["deck_id"] = self.current_deck_index
                        self.start_button.action["commander_id"] = self.current_commander_id
                        return self.start_button.action

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
                # Commander selection
                if self.commander_rect.collidepoint(event.pos):
                    self.open_carousel()

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
        cards_list = deck.get("cards", [])
        return [
            {
                "card": next(card for card in self.all_cards if card["id"] == entry["id"]),
                "count": entry["count"]
            }
            for entry in cards_list
        ]

    def get_commander_by_id(self, commander_id):
        for faction in self.factions_data:
            for commander in faction["commanders"]:
                if commander["id"] == commander_id:
                    return commander
        return None

    def set_commander(self, data):
        commander_id = data['card_id']
        self.current_commander_id = commander_id
        self.current_decks[self.current_deck_index]["commander_id"] = commander_id

    def update_filtered_cards(self):
        faction = self.factions[self.current_faction_index]
        self.filtered_cards = [card for card in self.all_cards if card["faction"] == faction or card["faction"] == "Neutralne"]
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

            total_strength += (card.get('power') or 0) * count


        return total_count, hero_count, special_count, total_strength

    def add_card_to_deck(self, card):
        deck = self.current_decks[self.current_deck_index]
        cards_list = deck["cards"]

        for entry in cards_list:
            if entry["id"] == card["id"]:
                if entry["count"] < card["count"]:
                    entry["count"] += 1
                    break
                else:
                    return
        else:
            cards_list.append({"id": card["id"], "count": 1})

    def remove_card_from_deck(self, card):
        deck = self.current_decks[self.current_deck_index]
        cards_list = deck["cards"]

        for entry in cards_list:
            if entry["id"] == card["id"]:
                if entry["count"] > 1:
                    entry["count"] -= 1
                else:
                    cards_list.remove(entry)
                break

    def can_start_game(self):
        total_count, hero_count, special_count, total_strength = self.calculate_deck_stats()
        if total_count >= 22 and special_count <= 10:
            return True
        return False

    def close_carousel(self):
        self.show_carousel = False
        self.carousel_scene = None

    def open_carousel(self):
        cards_to_show = self.factions_data[self.current_faction_index]["commanders"]
        self.carousel_scene = CarouselScene(self.screen, self.draw_card, cards_to_show, choose_count=1, cancelable=True)
        self.show_carousel = True

    def draw_card(self, card, x, y, size):
        image = load_card_image(card, size, self.factions[self.current_faction_index])
        rect = image.get_rect(topleft=(x, y))
        self.screen.blit(image, rect)
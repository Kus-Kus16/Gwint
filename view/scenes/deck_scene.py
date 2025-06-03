import json

import pygame
from overrides import overrides

from model import cards_database as db
from model.card import Card
from model.card_base import CardType
from view import constants as c
from view.components.button import Button
from view.constants import BUTTON_SIZE_WIDE
from view.scenes.carousel_scene import CarouselScene
from view.scenes.scene import Scene

CARD_MARGIN = 20
VISIBLE_CARDS = 6

ROWS = 2
COLS = 3
CARDS_PER_PAGE = ROWS * COLS

#TODO refactor
class DeckScene(Scene):
    def __init__(self, screen):
        super().__init__(screen)
        self.all_cards = db.card_dict
        self.scroll_offset = 0

        self.scroll_offset_all = 0
        self.scroll_offset_deck = 0

        self.current_faction_index = 0
        self.current_deck_index = 0

        # Decks
        with open("./user/user_decks.json", "r", encoding="utf-8") as file:
            self.current_decks = json.load(file)

        # Commander
        with open("./data/factions.json", "r", encoding="utf-8") as f:
            self.factions_data = json.load(f)
        self.factions = [f["name"] for f in self.factions_data][0:2] # TODO v1 2 decks only
        self.current_commander_id = self.current_decks[self.current_deck_index].get("commander_id", None)
        self.commander_rect= None

        self.carousel_scene = None
        self.show_carousel = False

        self.filtered_cards = None
        self.update_filtered_cards()

        # Click rects
        self.left_card_rects = []
        self.right_card_rects = []

        button_width, button_height = c.BUTTON_SIZE_NARROW
        self.back_button = Button("Menu",
                                  ((self.screen_width - button_width) // 2, self.screen_height - button_height - 30),
                                  c.BUTTON_SIZE_NARROW,
                                  {"type": "mode_change", "mode": "menu"})

        self.start_button = Button("Graj",
                                  ((self.screen_width - button_width) // 2, self.screen_height - button_height - 30 - button_height - 10),
                                  c.BUTTON_SIZE_NARROW,
                                  {"type": "mode_change", "mode": "load_deck", "deck_id": self.current_deck_index, "commander_id": self.current_commander_id})

        self.prev_faction_button = None
        self.next_faction_button = None
        self.update_faction_buttons()

        # Scrollbar
        self.dragging_scroll_all = False
        self.dragging_scroll_deck = False
        self.scroll_start_deck = None
        self.drag_start_y = None
        self.scroll_start_all = None
        self.scrollbar_width = 15

        self.darken = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.darken.fill((0, 0, 0, 218))


    def update_faction_buttons(self):
        prev_index = (self.current_faction_index - 1) % len(self.factions)
        next_index = (self.current_faction_index + 1) % len(self.factions)

        prev_name = self.factions[prev_index]
        next_name = self.factions[next_index]

        self.prev_faction_button = Button(f"< {prev_name}", (50, 50), BUTTON_SIZE_WIDE,
                                          {"type": "change_faction", "direction": -1},
                                          font=c.CINZEL_25_BOLD)
        self.next_faction_button = Button(f"{next_name} >", (self.screen_width - 450, 50), BUTTON_SIZE_WIDE,
                                          {"type": "change_faction", "direction": 1},
                                          font=c.CINZEL_25_BOLD)

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
            self.draw_commander()
            self.draw_scrollbar()

    def draw_scrollbar(self):
        # LEFT
        collection_x = 70 - self.scrollbar_width - 5
        collection_y = 270
        collection_height = ROWS * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN) - CARD_MARGIN
        content_length_left = len(self.filtered_cards)
        scroll_offset_left = self.scroll_offset_all

        if content_length_left > CARDS_PER_PAGE:
            proportion_visible = CARDS_PER_PAGE / content_length_left
            scrollbar_height = max(int(collection_height * proportion_visible), 20)
            max_scroll = content_length_left - CARDS_PER_PAGE
            scrollbar_pos = int((collection_height - scrollbar_height) * scroll_offset_left / max_scroll)

            pygame.draw.rect(self.screen, c.COLOR_GOLD,
                             (collection_x, collection_y, self.scrollbar_width, collection_height))
            pygame.draw.rect(self.screen, c.COLOR_BLACK,
                             (collection_x, collection_y + scrollbar_pos, self.scrollbar_width, scrollbar_height))

        # RIGHT
        deck_x = self.screen_width - 70 + 5
        deck_y = 270
        deck_height = ROWS * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN) - CARD_MARGIN
        deck_cards = self.get_deck_cards(self.current_deck_index)
        content_length_right = len(deck_cards)
        scroll_offset_right = self.scroll_offset_deck

        if content_length_right > CARDS_PER_PAGE:
            proportion_visible = CARDS_PER_PAGE / content_length_right
            scrollbar_height = max(int(deck_height * proportion_visible), 20)
            max_scroll = content_length_right - CARDS_PER_PAGE
            if max_scroll > 0:
                scrollbar_pos = int((deck_height - scrollbar_height) * scroll_offset_right / max_scroll)
            else:
                scrollbar_pos = 0

            pygame.draw.rect(self.screen, c.COLOR_GOLD,
                             (deck_x, deck_y, self.scrollbar_width, deck_height))
            pygame.draw.rect(self.screen, c.COLOR_BLACK,
                             (deck_x, deck_y + scrollbar_pos, self.scrollbar_width, scrollbar_height))
        else:
            pygame.draw.rect(self.screen, c.COLOR_GOLD,
                             (deck_x, deck_y, self.scrollbar_width, deck_height))
            pygame.draw.rect(self.screen, c.COLOR_BLACK,
                             (deck_x, deck_y, self.scrollbar_width, deck_height))

    def draw_commander(self):
        commander = self.get_commander_by_id(self.current_commander_id)
        if commander:
            commander_image = self.load_card_image(commander, "medium")
            self.screen.blit(commander_image, (self.screen_width // 2 - c.MEDIUM_CARD_SIZE[0] // 2, 170))
            commander_pos = (self.screen_width // 2 - c.MEDIUM_CARD_SIZE[0] // 2, 170)
            self.commander_rect = pygame.Rect(commander_pos, c.MEDIUM_CARD_SIZE)

    def draw_buttons(self):
        self.prev_faction_button.draw(self.screen, pygame.mouse.get_pos())
        self.next_faction_button.draw(self.screen, pygame.mouse.get_pos())
        self.back_button.draw(self.screen, pygame.mouse.get_pos())
        self.start_button.draw(self.screen, pygame.mouse.get_pos())

    def draw_texts(self):
        # Titles
        font = c.CINZEL_30_BOLD
        text_surface = font.render(f"Kolekcja kart", True, c.COLOR_GOLD)
        self.screen.blit(text_surface, (50, 180))
        text_surface = font.render(f"Karty w talii", True, c.COLOR_GOLD)
        self.screen.blit(text_surface, (self.screen_width - text_surface.get_width() - 50, 180))
        # Faction name
        font = c.CINZEL_50_BOLD
        faction_name = self.factions[self.current_faction_index]
        text_surface = font.render(f"Frakcja: {faction_name}", True, c.COLOR_GOLD)
        self.screen.blit(text_surface, (self.screen_width // 2 - text_surface.get_width() // 2, 50))
        # Commander
        commander = self.get_commander_by_id(self.current_commander_id)
        if commander:
            font = c.CINZEL_30_BOLD
            text_surface = font.render("Dowódca", True, c.COLOR_GOLD)
            self.screen.blit(text_surface, (self.screen_width // 2 - text_surface.get_width() // 2, 130))

    def show_deck_stats(self):
        total_count, hero_count, special_count, total_strength = self.calculate_deck_stats()
        stats_font = c.CINZEL_30_BOLD
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
            color = c.COLOR_GOLD
            if i == 1:  # Total count
                color = c.COLOR_GREEN if total_count >= 22 else c.COLOR_RED
            elif i == 5:  # Special count
                color = c.COLOR_GREEN if special_count <= 10 else c.COLOR_RED

            stats_surface = stats_font.render(line, True, color)
            stats_x = self.screen_width // 2 - stats_surface.get_width() // 2
            stats_y = start_y + i * (line_height + 3)
            self.screen.blit(stats_surface, (stats_x, stats_y))

    def show_deck_cards(self):
        deck_cards = self.get_deck_cards(self.current_deck_index)

        self.right_card_rects = []
        visible_deck_cards = deck_cards[self.scroll_offset_deck:self.scroll_offset_deck + CARDS_PER_PAGE]

        for idx, entry in enumerate(visible_deck_cards):
            card = entry["card"]
            image = self.load_card_image(card, "medium")
            row = idx // COLS
            col = idx % COLS
            total_width = COLS * c.MEDIUM_CARD_SIZE[0] + (COLS - 1) * CARD_MARGIN
            x_start = self.screen_width - total_width - 70
            x = x_start + col * (c.MEDIUM_CARD_SIZE[0] + CARD_MARGIN)
            y = 270 + row * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN)
            self.screen.blit(image, (x, y))
            self.right_card_rects.append((pygame.Rect(x, y, *c.MEDIUM_CARD_SIZE), card))

            count = entry["count"]
            if count > 1:
                overlay = pygame.Surface((60, 36), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 190))
                overlay_x = x + c.MEDIUM_CARD_SIZE[0] - 60 - 10
                overlay_y = y + 10
                self.screen.blit(overlay, (overlay_x, overlay_y))
                self.draw_text(count, overlay_x + 30, overlay_y + 18, center=True)

    def show_all_available_cards(self):
        self.left_card_rects = []
        visible_cards = self.filtered_cards[self.scroll_offset_all:self.scroll_offset_all + CARDS_PER_PAGE]
        for idx, card in enumerate(visible_cards):
            image = self.load_card_image(card, "medium")
            row = idx // COLS
            col = idx % COLS
            x = 70 + col * (c.MEDIUM_CARD_SIZE[0] + CARD_MARGIN)
            y = 270 + row * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN)
            self.screen.blit(image, (x, y))
            self.left_card_rects.append((pygame.Rect(x, y, *c.MEDIUM_CARD_SIZE), card))

    @overrides
    def handle_events(self, event):
        if self.show_carousel:
            result = self.carousel_scene.handle_events(event)
            if result is not None:
                self.set_commander(result)
                self.close_carousel()
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if event.button == 1:
                # Scrollbar
                # Left
                collection_x = 70 - self.scrollbar_width - 5
                collection_y = 270
                collection_height = ROWS * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN) - CARD_MARGIN
                if (collection_x <= mouse_x <= collection_x + self.scrollbar_width) and (
                     collection_y <= mouse_y <= collection_y + collection_height):
                    self.dragging_scroll_all = True
                    self.drag_start_y = mouse_y
                    self.scroll_start_all = self.scroll_offset_all
                    return

                # Right
                deck_x = self.screen_width - 70 + 5
                deck_y = 270
                deck_height = ROWS * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN) - CARD_MARGIN
                if (deck_x <= mouse_x <= deck_x + self.scrollbar_width) and (deck_y <= mouse_y <= deck_y + deck_height):
                    self.dragging_scroll_deck = True
                    self.drag_start_y = mouse_y
                    self.scroll_start_deck = self.scroll_offset_deck
                    return

                # Back button
                if self.back_button.check_click(event.pos):
                    self.lock()
                    with open("./user/user_decks.json", "w", encoding="utf-8") as f:
                        json.dump(self.current_decks, f, ensure_ascii=False, indent=4)
                    return self.back_button.action

                # Start button
                if self.can_start_game():
                    if self.start_button.check_click(event.pos):
                        self.lock()
                        with open("./user/user_decks.json", "w", encoding="utf-8") as f:
                            json.dump(self.current_decks, f, ensure_ascii=False, indent=4)
                        self.start_button.action["deck_id"] = self.current_deck_index
                        self.start_button.action["commander_id"] = self.current_commander_id
                        return self.start_button.action

                # Prev faction button
                if self.prev_faction_button.check_click(event.pos):
                    self.current_faction_index = (self.current_faction_index - 1) % len(self.factions)
                    self.current_deck_index = self.current_faction_index
                    self.current_commander_id = self.current_decks[self.current_deck_index].get("commander_id", None)
                    self.update_filtered_cards()
                    self.update_faction_buttons()
                    self.scroll_offset_deck = 0

                # Next faction button
                if self.next_faction_button.check_click(event.pos):
                    self.current_faction_index = (self.current_faction_index + 1) % len(self.factions)
                    self.current_deck_index = self.current_faction_index
                    self.current_commander_id = self.current_decks[self.current_deck_index].get("commander_id", None)
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
                    if event.button == 4:  # Scroll up
                        self.scroll_offset_deck = max(0, self.scroll_offset_deck - COLS)
                    elif event.button == 5:  # Scroll down
                        max_scroll = max(0, len(deck_cards) - CARDS_PER_PAGE)
                        self.scroll_offset_deck = min(max_scroll, self.scroll_offset_deck + COLS)

        # Scrollbar dragging
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_scroll_all = False
                self.dragging_scroll_deck = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_scroll_all:
                mouse_x, mouse_y = event.pos
                collection_height = ROWS * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN) - CARD_MARGIN
                max_scroll = max(0, len(self.filtered_cards) - CARDS_PER_PAGE)
                if max_scroll == 0:
                    return

                delta_y = mouse_y - self.drag_start_y
                scroll_range = collection_height - max(20, int(collection_height * CARDS_PER_PAGE / len(
                    self.filtered_cards)))
                scroll_delta = int(delta_y * max_scroll / scroll_range)
                new_offset = self.scroll_start_all + scroll_delta
                self.scroll_offset_all = max(0, min(max_scroll, new_offset))

            elif self.dragging_scroll_deck:
                mouse_x, mouse_y = event.pos
                deck_height = ROWS * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN) - CARD_MARGIN
                deck_cards = self.get_deck_cards(self.current_deck_index)
                max_scroll = max(0, len(deck_cards) - CARDS_PER_PAGE)
                if max_scroll == 0:
                    return

                delta_y = mouse_y - self.drag_start_y
                scroll_range = deck_height - max(20, int(deck_height * CARDS_PER_PAGE / len(deck_cards)))
                scroll_delta = int(delta_y * max_scroll / scroll_range)
                new_offset = self.scroll_start_deck + scroll_delta
                self.scroll_offset_deck = max(0, min(max_scroll, new_offset))

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

        if commander_id is None:
            return

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
            card = Card(entry["card"])
            count = entry["count"]
            if card.is_card_type(CardType.HERO) or card.is_card_type(CardType.UNIT):
                total_count += count

            if card.is_card_type(CardType.HERO):
                hero_count += count
            if card.power is None:
                special_count += count
            else:
                total_strength += card.power * count

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
        self.carousel_scene = CarouselScene(self.screen, self.draw_card, cards_to_show, choose_count=1, cancelable=True, label=False)
        self.show_carousel = True

    @overrides
    def get_card_paths(self, card, size):
        faction = self.factions[self.current_faction_index]
        filename = card["filename"]
        return faction, filename

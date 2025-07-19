import json

import pygame
from overrides import overrides

from model import cards_database as db
from model.card import Card
from model.enums.card_type import CardType
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

class DeckScene(Scene):
    def __init__(self, screen):
        super().__init__(screen)

        self.scroll_offset = 0
        self.scroll_offset_all = 0
        self.scroll_offset_deck = 0

        # Decks
        with open("./user/user_decks.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            self.current_decks = data["decks"]
            self.current_deck_index = data.get("last_index", 0)
            self.current_faction_index = data.get("last_index", 0)

        # Commander
        with open("./data/factions.json", "r", encoding="utf-8") as f:
            self.factions_data = json.load(f)

        self.factions = [f["name"] for f in self.factions_data][0:2] # TODO v1 2 decks only
        self.current_commander_id = self.current_decks[self.current_deck_index].get("commander_id", None)
        self.commander_rect = None

        self.carousel_scene = None
        self.show_carousel = False

        self.filtered_cards = None
        self.update_filtered_cards()

        # Click rects
        self.left_card_rects = []
        self.right_card_rects = []

        # Buttons
        self.back_button = None
        self.start_button = None
        self.prev_faction_button = None
        self.next_faction_button = None

        self._init_ui_buttons()

        # Scroll
        self.dragging_scroll_all = False
        self.dragging_scroll_deck = False
        self.scroll_start_deck = None
        self.drag_start_y = None
        self.scroll_start_all = None
        self.scrollbar_width = 15

    def _init_ui_buttons(self):
        button_width, button_height = c.BUTTON_SIZE_NARROW
        self.back_button = Button("Menu",
                                  ((self.screen_width - button_width) // 2, self.screen_height - button_height - 30),
                                  c.BUTTON_SIZE_NARROW,
                                  {"type": "mode_change", "mode": "menu"})
        self.start_button = Button("Graj",
                                   ((self.screen_width - button_width) // 2,
                                    self.screen_height - button_height - 30 - button_height - 10),
                                   c.BUTTON_SIZE_NARROW,
                                   {"type": "mode_change", "mode": "load_deck", "deck_id": self.current_deck_index,
                                    "commander_id": self.current_commander_id})
        self.update_faction_buttons()

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
        super().draw()
        self.draw_overlay(0.85)
        self.draw_texts()
        self.show_all_available_cards()
        self.show_deck_cards()
        self.show_deck_stats()
        self.draw_buttons()
        self.draw_commander()
        self.draw_scrollbar()

        if self.show_carousel:
            self.carousel_scene.draw()

    def draw_scrollbar(self):
        def draw_single_scrollbar(x, y, height, content_length, scroll_offset):
            if content_length > CARDS_PER_PAGE:
                proportion_visible = CARDS_PER_PAGE / content_length
                scrollbar_height = max(int(height * proportion_visible), 20)
                max_scroll = content_length - CARDS_PER_PAGE
                scrollbar_pos = int((height - scrollbar_height) * scroll_offset / max_scroll)

                pygame.draw.rect(self.screen, c.COLOR_GOLD,
                                 (x, y, self.scrollbar_width, height))
                pygame.draw.rect(self.screen, c.COLOR_BLACK,
                                 (x, y + scrollbar_pos, self.scrollbar_width, scrollbar_height))
        # LEFT
        collection_x = 70 - self.scrollbar_width - 5
        collection_y = 270
        collection_height = ROWS * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN) - CARD_MARGIN
        content_length_left = len(self.filtered_cards)
        scroll_offset_left = self.scroll_offset_all

        draw_single_scrollbar(collection_x, collection_y, collection_height,
                                   content_length_left, scroll_offset_left)

        # RIGHT
        deck_x = self.screen_width - 70 + 5
        deck_y = 270
        deck_height = ROWS * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN) - CARD_MARGIN
        content_length_right = len(self.get_deck_cards(self.current_deck_index))
        scroll_offset_right = self.scroll_offset_deck

        draw_single_scrollbar(deck_x, deck_y, deck_height,
                                   content_length_right, scroll_offset_right)

    def draw_commander(self):
        commander, _ = db.find_commander_by_id(self.current_commander_id)
        if commander:
            x = (self.screen_width - c.MEDIUM_CARD_SIZE[0]) // 2
            y = 170
            self.commander_rect = self.draw_card(commander, x, y, "medium")

    def draw_buttons(self):
        self.prev_faction_button.draw(self.screen, pygame.mouse.get_pos())
        self.next_faction_button.draw(self.screen, pygame.mouse.get_pos())
        self.back_button.draw(self.screen, pygame.mouse.get_pos())
        self.start_button.draw(self.screen, pygame.mouse.get_pos())

    def draw_texts(self):
        # Titles
        font = c.CINZEL_30_BOLD
        color = c.COLOR_GOLD
        self.draw_text("Kolekcja Kart", 50, 180, color=color, font=font)
        self.draw_text("Karty w Talii", 1820, 180, color=color, font=font) #TODO change to center

        # Commander
        self.draw_text("Dowódca", self.screen_width // 2, 130, color=color, font=font, center=True)

        # Faction name
        font = c.CINZEL_50_BOLD
        faction_name = self.get_faction_name()
        self.draw_text(f"Frakcja: {faction_name}", self.screen_width // 2, 50, color=color, font=font, center=True)

    def show_deck_stats(self):
        total_count, hero_count, special_count, total_strength = self.calculate_deck_stats()
        font = c.CINZEL_30_BOLD

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

        start_y = 550
        y_offset = 30
        for i, line in enumerate(lines):
            if i == 1:  # Total count
                color = c.COLOR_GREEN if total_count >= 22 else c.COLOR_RED
            elif i == 5:  # Special count
                color = c.COLOR_GREEN if special_count <= 10 else c.COLOR_RED
            else:
                color = c.COLOR_GOLD

            y = start_y + i * y_offset
            self.draw_text(line, self.screen_width // 2, y, color=color, font=font, center=True)

    #Todo change
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

    #Todo change
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
            if event.button == 1:
                return self.handle_leftclick(event)

            elif event.button in (4, 5):
                return self.handle_scroll(event)

        # Scrollbar dragging
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_scroll_all = False
                self.dragging_scroll_deck = False

        elif event.type == pygame.MOUSEMOTION:
            return self.handle_mousemotion(event)

    def handle_leftclick(self, event):
        mouse_x, mouse_y = event.pos

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
            self.save_user_deck()
            return self.back_button.action

        # Start button
        if self.start_button.check_click(event.pos) and self.can_start_game():
            self.lock()
            self.save_user_deck()
            self.start_button.action["deck_id"] = self.current_deck_index
            self.start_button.action["commander_id"] = self.current_commander_id
            return self.start_button.action

        # Prev faction button
        if self.prev_faction_button.check_click(event.pos):
            self.change_faction(-1)
        # Next faction button
        if self.next_faction_button.check_click(event.pos):
            self.change_faction(1)

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

    def handle_scroll(self, event):
        def update_scroll_offset(scroll_attr_name, content_length, button):
            scroll_offset = getattr(self, scroll_attr_name)
            if button == 4:  # Scroll up
                scroll_offset = max(0, scroll_offset - COLS)
            elif button == 5:  # Scroll down
                max_scroll = max(0, content_length - CARDS_PER_PAGE)
                scroll_offset = min(max_scroll, scroll_offset + COLS)
            setattr(self, scroll_attr_name, scroll_offset)

        mouse_x, _ = pygame.mouse.get_pos()
        is_left_side = mouse_x < self.screen_width // 2

        if is_left_side:
            update_scroll_offset("scroll_offset_all", len(self.filtered_cards), event.button)
        else:
            deck_cards = self.get_deck_cards(self.current_deck_index)
            update_scroll_offset("scroll_offset_deck", len(deck_cards), event.button)

    def handle_mousemotion(self, event):
        def update_drag_scroll(dragging, drag_start_y, scroll_start, content_length, height, set_offset):
            if not dragging:
                return

            max_scroll = max(0, content_length - CARDS_PER_PAGE)
            if max_scroll == 0:
                return

            delta_y = event.pos[1] - drag_start_y
            visible_ratio = CARDS_PER_PAGE / content_length
            scrollbar_height = max(20, int(height * visible_ratio))
            scroll_range = height - scrollbar_height
            scroll_delta = int(delta_y * max_scroll / scroll_range)
            new_offset = scroll_start + scroll_delta
            set_offset(max(0, min(max_scroll, new_offset)))

        # Left scrollbar
        update_drag_scroll(
            self.dragging_scroll_all,
            self.drag_start_y,
            self.scroll_start_all,
            len(self.filtered_cards),
            ROWS * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN) - CARD_MARGIN,
            lambda v: setattr(self, "scroll_offset_all", v)
        )

        # Right scrollbar
        update_drag_scroll(
            self.dragging_scroll_deck,
            self.drag_start_y,
            self.scroll_start_deck,
            len(self.get_deck_cards(self.current_deck_index)),
            ROWS * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN) - CARD_MARGIN,
            lambda v: setattr(self, "scroll_offset_deck", v)
        )

    def change_faction(self, direction):
        self.current_faction_index = (self.current_faction_index + direction) % len(self.factions)
        self.current_deck_index = self.current_faction_index
        self.current_commander_id = self.current_decks[self.current_deck_index].get("commander_id", None)
        self.update_filtered_cards()
        self.update_faction_buttons()
        self.scroll_offset_deck = 0

    # noinspection PyTypeChecker
    def save_user_deck(self):
        with open("./user/user_decks.json", "w", encoding="utf-8") as f:
            json.dump({
                "decks": self.current_decks,
                "last_index": self.current_deck_index
            }, f, ensure_ascii=False, indent=4)

    def get_deck_cards(self, index):
        deck = self.current_decks[index]
        cards_list = deck.get("cards", [])
        return [
            {
                "card": db.find_card_by_id(entry["id"]),
                "count": entry["count"]
            }
            for entry in cards_list
        ]

    def set_commander(self, data):
        commander_id = data['card_id']

        if commander_id is None:
            return

        self.current_commander_id = commander_id
        self.current_decks[self.current_deck_index]["commander_id"] = commander_id

    def update_filtered_cards(self):
        faction = self.get_faction_name()
        self.filtered_cards = db.get_faction_cards(faction, neutral=True)
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
        self.carousel_scene = CarouselScene(self.screen, self.draw_card, cards_to_show,
                                            choose_count=1, cancelable=True, label=False, opacity=0.75,
                                            get_card_attr=self.get_card_attr)
        self.show_carousel = True

    @overrides
    def get_card_paths(self, card, size):
        faction = self.get_faction_name()
        filename = card["filename"]
        return faction, filename

    @staticmethod
    @overrides
    def get_card_attr(card, attrname):
        return card[attrname]

    def get_faction_name(self):
        return self.factions[self.current_faction_index]
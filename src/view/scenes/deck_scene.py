import pygame
from overrides import overrides

from src.model.card_holders.sorted_card_holder import SortedCardHolder
from src.model.cards import cards_database as db
from src.model.cards.card_entry import CardEntry
from src.model.cards.commander_entry import CommanderEntry
from src.model.enums.card_type import CardType
from src.model.enums.faction_type import FactionType
from src.view import loader, saver
from src.view.components.scrollbar import Scrollbar
from src.view.constants import deck_constants as c, ui_constants as u
from src.view.components.button import Button
from src.view.scenes.carousel_scene import CarouselScene
from src.view.scenes.scene import Scene

class DeckScene(Scene):
    def __init__(self, screen):
        super().__init__(screen)
        self.stats = {
            "total_count": 0,
            "unit_count": 0,
            "special_count": 0,
            "total_strength": 0,
            "hero_count": 0,
        }

        # Click rects
        self.commander_rect = None
        self.left_card_rects = []
        self.right_card_rects = []

        # Scroll
        self.scrollbar_left = Scrollbar(c.LEFT_SCROLLBAR_POS, c.SCROLLBAR_HEIGHT, u.COLOR_GRAY)
        self.scrollbar_right = Scrollbar(c.RIGHT_SCROLLBAR_POS, c.SCROLLBAR_HEIGHT, u.COLOR_GRAY)

        # Buttons
        button_width, button_height = u.BUTTON_SIZE_NARROW
        x, y = (self.screen_width - button_width) // 2, self.screen_height - button_height - 30

        self.buttons = [
            Button("Menu", (x, y), u.BUTTON_SIZE_NARROW, self.button_menu),
            Button("Graj", (x, y - button_height - 10), u.BUTTON_SIZE_NARROW, self.button_play)
        ]

        # Factions
        self.factions = [faction for faction in FactionType if faction != FactionType.NEUTRALNE]
        self.all_decks = {
            faction: {"left": SortedCardHolder(), "right": SortedCardHolder()}
            for faction in self.factions
        }

        userdata = loader.load_data("user_decks", is_userdata=True)
        self.current_deck_index = 0
        self.init_decks(userdata)

    def init_decks(self, userdata):
        for faction in self.factions:
            self.change_faction(faction=faction)
            decks = self.get_current_deck_dict()

            card_list = db.get_faction_cards(faction, include_neutral=True)
            commander_data = db.get_faction_commanders(faction)[0]
            decks["commander"] = CommanderEntry(commander_data)
            holder = decks["left"]

            for card_data in card_list:
                card = CardEntry(card_data)
                holder.add_card(card)

        user_decks = userdata["decks"]
        final_faction = None
        for i, deck in enumerate(user_decks):
            faction = FactionType.fullname_to_faction(deck["faction"])
            self.change_faction(faction=faction)

            self.set_commander(deck["commander_id"])

            for card_data in deck["cards"]:
                self.move_to_right(card_data["id"], card_data["count"])

            if i == userdata["last_used_index"]:
                final_faction = faction

        if final_faction:
            self.change_faction(faction=final_faction)

    def update_faction_buttons(self):
        prev_index = (self.current_deck_index - 1) % len(self.factions)
        next_index = (self.current_deck_index + 1) % len(self.factions)

        prev_name = FactionType.faction_to_fullname(self.factions[prev_index])
        next_name = FactionType.faction_to_fullname(self.factions[next_index])

        y = c.TOP_BUTTONS_Y - u.BUTTON_SIZE_WIDE[1] // 2
        buttons = [
            Button(f"<< {prev_name}", (50, y), u.BUTTON_SIZE_WIDE,
                   self.button_prev, font=u.CINZEL_25_BOLD),
            Button(f"{next_name} >>", (self.screen_width - 450, y), u.BUTTON_SIZE_WIDE,
                   self.button_next, font=u.CINZEL_25_BOLD)
        ]
        self.buttons[2:] = buttons

    @overrides
    def draw(self):
        super().draw()
        self.draw_overlay(0.85)
        self.draw_texts()
        self.draw_left_cards()
        self.draw_right_cards()
        self.draw_deck_stats()
        self.draw_buttons()
        self.draw_commander()
        self.draw_scrollbars()
        self.draw_temporary()

    def draw_scrollbars(self):
        deck_dict = self.get_current_deck_dict()

        self.scrollbar_left.draw(self.screen, deck_dict["left"].size())
        self.scrollbar_right.draw(self.screen, deck_dict["right"].size())

    def draw_commander(self):
        self.draw_text("Dowódca", *c.COMM_LABEL_POS, color=u.COLOR_GOLD, font=u.CINZEL_25_BOLD, center=True)

        commander = self.get_current_deck_dict().get("commander")
        if commander:
            x = (self.screen_width - u.MEDIUM_CARD_SIZE[0]) // 2
            self.commander_rect = self.draw_card(commander, x, c.COMM_Y, "medium")

    def draw_buttons(self):
        mouse_pos = pygame.mouse.get_pos()
        for button in list(self.buttons):
            button.draw(self.screen, mouse_pos)

    def draw_texts(self):
        # Titles
        font = u.CINZEL_25_BOLD
        color = u.COLOR_WHITE

        self.draw_text("Kolekcja Kart", *c.LEFT_LABEL_POS, color=color, font=font)
        self.draw_text("Karty w Talii", *c.RIGHT_LABEL_POS, color=color, font=font)

        # Faction name
        font = u.CINZEL_50_BOLD
        faction_name = FactionType.faction_to_fullname(self.get_faction())
        self.draw_text(faction_name, self.screen_width // 2, c.TOP_BUTTONS_Y, color=color, font=font, center=True)

    def draw_single_stat(self, y, ico_filename, text, value, color):
        x_center = self.screen_width // 2
        self.draw_text(text, x_center, y, color=u.COLOR_LIGHTGRAY, font=u.CINZEL_20_BOLD, center=True)

        y_center = y + 30
        self.draw_icon(ico_filename, None, x_center - 25, y_center, center=True)
        self.draw_text(value, x_center + 25, y_center, font=u.CINZEL_25, color=color, center=True)

    def draw_deck_stats(self):
        lines = [
            ("Wszystkie karty w talii", self.stats["total_count"], "deck_count"),
            ("Liczba kart jednostek", self.stats["unit_count"], "deck_unit"),
            ("Karty specjalne", f"{self.stats['special_count']}/10", "deck_special"),
            ("Całkowita siła jednostek", self.stats["total_strength"], "deck_strength"),
            ("Karty bohaterów", self.stats["hero_count"], "deck_hero"),
        ]

        start_y = c.STATS_Y
        y_offset = 60

        for i, (text, value, filename) in enumerate(lines):
            color = u.COLOR_GOLD
            if i == 1 and self.stats["unit_count"] < 22:  # Unit count
                color = u.COLOR_RED
            elif i == 2:  # Special count
                color = u.COLOR_RED if self.stats["special_count"] > 10 else u.COLOR_GREEN

            y = start_y + i * y_offset
            self.draw_single_stat(y, filename, text, value, color)

    def draw_cards_pane(self, cards, rect_output, start_pox, scroll_offset):
        rect_output.clear()

        visible_deck_cards = cards[scroll_offset:scroll_offset + c.CARDS_PER_PAGE]
        x_start, y_start = start_pox

        for idx, card in enumerate(visible_deck_cards):
            row = idx // c.COL_COUNT
            col = idx % c.COL_COUNT

            x = x_start + col * (u.MEDIUM_CARD_SIZE[0] + c.CARD_MARGIN)
            y = y_start + row * (u.MEDIUM_CARD_SIZE[1] + c.CARD_MARGIN)

            rect = self.draw_card(card, x, y, "medium")
            rect_output.append((rect, card))

            overlay_x = x + u.MEDIUM_CARD_SIZE[0] - 60 - 10
            overlay_y = y + 10
            self.draw_label(card.count, overlay_x, overlay_y)

    def draw_left_cards(self):
        cards = self.get_current_deck_dict()["left"].cards
        self.draw_cards_pane(cards, self.left_card_rects, c.LEFT_START_POS, self.scrollbar_left.offset)

    def draw_right_cards(self):
        cards = self.get_current_deck_dict()["right"].cards
        self.draw_cards_pane(cards, self.right_card_rects, c.RIGHT_START_POS, self.scrollbar_right.offset)

    @overrides
    def handle_events(self, event):
        if self.temporary_drawable:
            result = self.handle_temporary(event)
            if result is not None:
                self.set_commander(result["card_id"])
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
                self.scrollbar_left.dragging = False
                self.scrollbar_right.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            return self.handle_mousemotion(event)

    def handle_leftclick(self, event):
        mouse_x, mouse_y = event.pos

        # Scrollbars
        for scrollbar in [self.scrollbar_left, self.scrollbar_right]:
            if scrollbar.check_click(event.pos):
                scrollbar.dragging = True
                scrollbar.drag_start_y = mouse_y
                scrollbar.scroll_start = scrollbar.offset
                return

        # Buttons
        for button in list(self.buttons):
            if button.check_click(event.pos):
                return button.on_click()

        # Commander selection
        if self.commander_rect.collidepoint(event.pos):
            self.open_carousel()
            return

        # Add card to deck
        for rect, card in self.left_card_rects:
            if rect.collidepoint(event.pos):
                self.move_to_right(card.id, 1)
                return

        # Remove card from deck
        for rect, card in self.right_card_rects:
            if rect.collidepoint(event.pos):
                self.move_to_left(card.id, 1)
                return

    def handle_scroll(self, event):
        mouse_x, _ = pygame.mouse.get_pos()
        is_left_side = mouse_x < self.screen_width // 2

        if is_left_side:
            cards = self.get_current_deck_dict()["left"]
            self.scrollbar_left.update_offset(cards.size(), event.button)
        else:
            cards = self.get_current_deck_dict()["right"]
            self.scrollbar_right.update_offset(cards.size(), event.button)

    def handle_mousemotion(self, event):
        deck_dict = self.get_current_deck_dict()
        event_y = event.pos[1]
        self.scrollbar_left.update_drag_scroll(deck_dict["left"].size(), event_y)
        self.scrollbar_right.update_drag_scroll(deck_dict["right"].size(), event_y)

    def button_menu(self):
        self.lock()
        self.save_user_deck()
        return {
            "type": "mode_change",
            "mode": "menu"
        }

    def button_play(self):
        self.lock()
        self.save_user_deck()
        return {
            "type": "mode_change",
            "mode": "new_game",
            "load": True
        }

    def button_prev(self):
        self.change_faction(direction=-1)

    def button_next(self):
        self.change_faction(direction=+1)

    def change_faction(self, direction=0, faction=None):
        if faction:
            self.current_deck_index = self.factions.index(faction)
            direction = 0

        self.current_deck_index = (self.current_deck_index + direction) % len(self.factions)
        self.update_faction_buttons()
        self.calculate_deck_stats()

        self.scrollbar_left.offset = 0
        self.scrollbar_right.offset = 0

    def save_user_deck(self):
        last_used_index = self.current_deck_index
        decks = []

        for faction in self.factions:
            self.change_faction(faction=faction)
            current_deck = self.get_current_deck_dict()
            dump_deck = dict()

            dump_deck["faction"] = FactionType.faction_to_fullname(self.get_faction())
            dump_deck["commander_id"] = current_deck["commander"].dump()
            dump_deck["cards"] = [card.dump() for card in current_deck["right"].cards]

            decks.append(dump_deck)

        self.change_faction(faction=self.factions[last_used_index])
        saver.save_userdata("user_decks", {"last_used_index": last_used_index, "decks": decks})

    def set_commander(self, commander_id):
        if commander_id is None:
            return

        commander_data = db.find_commander_by_id(commander_id)
        self.get_current_deck_dict()["commander"] = CommanderEntry(commander_data)

    def calculate_deck_stats(self):
        deck = self.get_current_deck_dict()["right"]
        stats = {
            "total_count": 0,
            "unit_count": 0,
            "special_count": 0,
            "total_strength": 0,
            "hero_count": 0,
        }

        for card in deck.cards:
            count = card.count
            self.update_stats(card, count, +1, stats)

        self.stats.update(stats)

    @classmethod
    def update_stats(cls, card, count, sign, dictionary):
        dictionary["total_count"] += count

        if card.is_card_type(CardType.SPECIAL):
            dictionary["special_count"] += count * sign
        elif card.is_card_type(CardType.UNIT) or card.is_card_type(CardType.HERO):
            dictionary["unit_count"] += count * sign
            dictionary["total_strength"] += card.power * count * sign

        if card.is_card_type(CardType.HERO):
            dictionary["hero_count"] += count * sign

    def get_current_deck_dict(self):
        current_faction = self.get_faction()
        return self.all_decks[current_faction]

    def move_cards(self, origin, source, id, count, stats_sign):
        deck = self.get_current_deck_dict()
        origin = deck[origin]
        source = deck[source]

        origin_card = origin.find_card_by_id(id)
        if not origin_card:
            return

        count = min(count, origin_card.count)
        origin_card.count -= count

        if origin_card.count <= 0:
            origin.remove_card(origin_card)

        source_card = source.find_card_by_id(id)
        if not source_card:
            source_card = origin_card.copy(0)
            source.add_card(source_card)

        source_card.count += count

        self.update_stats(origin_card, count, stats_sign, self.stats)

    def move_to_left(self, id, count):
        self.move_cards("right", "left", id, count, -1)

    def move_to_right(self, id, count):
        self.move_cards("left", "right", id, count, +1)

    def can_start_game(self):
        if self.stats["total_count"] < 22 or self.stats["special_count"] > 10:
            return False

        return True

    def close_carousel(self):
        self.pop_temporary()

    def open_carousel(self):
        cards_data = db.get_faction_commanders(self.get_faction())
        commanders = [CommanderEntry(data) for data in cards_data]

        initial_index = 0
        current_commander_id = self.get_current_deck_dict()["commander"].id
        for i, commander in enumerate(commanders):
            if commander.id == current_commander_id:
                initial_index = i
                break

        carousel = CarouselScene(self.screen, commanders, self.get_card_paths, initial_index=initial_index,
                                            choose_count=1, cancelable=True, opacity=0.75)
        self.add_temporary(carousel)

    def get_faction(self):
        return self.factions[self.current_deck_index]

    @overrides
    def get_card_paths(self, card, size):
        faction = card.faction
        if faction is FactionType.NEUTRALNE:
            faction = self.get_faction()

        faction = FactionType.faction_to_fullname(faction)
        filename = card.filename
        return faction, filename
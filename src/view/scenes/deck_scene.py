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
        self.carousel_scene = None

        # Click rects
        self.commander_rect = None
        self.left_card_rects = []
        self.right_card_rects = []

        # Scroll
        self.scrollbar_left = Scrollbar(c.LEFT_SCROLLBAR_POS, c.SCROLLBAR_HEIGHT, u.COLOR_GRAY)
        self.scrollbar_right = Scrollbar(c.RIGHT_SCROLLBAR_POS, c.SCROLLBAR_HEIGHT, u.COLOR_GRAY)

        # Factions
        self.factions = [faction for faction in FactionType if faction != FactionType.NEUTRALNE]
        self.all_decks = {
            faction: {"left": SortedCardHolder(), "right": SortedCardHolder()}
            for faction in self.factions
        }

        userdata = loader.load_data("user_decks", is_userdata=True)
        self.current_deck_index = 0
        self.init_decks(userdata)

        # Buttons
        self.prev_faction_button = None
        self.next_faction_button = None

        button_width, button_height = u.BUTTON_SIZE_NARROW
        x, y = (self.screen_width - button_width) // 2, self.screen_height - button_height - 30
        self.back_button = Button("Menu",(x, y), u.BUTTON_SIZE_NARROW,
                                  {"type": "mode_change", "mode": "menu"})
        self.start_button = Button("Graj", (x, y - button_height - 10), u.BUTTON_SIZE_NARROW,
                                   {"type": "mode_change", "mode": "new_game", "load": True})
        self.update_faction_buttons()

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
        self.prev_faction_button = Button(f"<< {prev_name}", (50, y), u.BUTTON_SIZE_WIDE,
                                          None, font=u.CINZEL_25_BOLD)
        self.next_faction_button = Button(f"{next_name} >>", (self.screen_width - 450, y), u.BUTTON_SIZE_WIDE,
                                          None, font=u.CINZEL_25_BOLD)

    @overrides
    def draw(self):
        super().draw()
        self.draw_overlay(0.85)
        self.draw_texts()
        self.draw_left_cards()
        self.draw_right_cards()
        self.show_deck_stats()
        self.draw_buttons()
        self.draw_commander()
        self.draw_scrollbars()

        if self.carousel_scene:
            self.carousel_scene.draw()

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
        self.prev_faction_button.draw(self.screen, mouse_pos)
        self.next_faction_button.draw(self.screen, mouse_pos)
        self.back_button.draw(self.screen, mouse_pos)
        self.start_button.draw(self.screen, mouse_pos)

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

    def show_deck_stats(self):
        total_count, unit_count, special_count, total_strength, hero_count = self.calculate_deck_stats()
        lines = [
            ("Wszystkie karty w talii", total_count, "deck_count"),
            ("Liczba kart jednostek", unit_count, "deck_unit"),
            ("Karty specjalne", f"{special_count}/10", "deck_special"),
            ("Całkowita siła jednostek", total_strength, "deck_strength"),
            ("Karty bohaterów", hero_count, "deck_hero"),
        ]

        start_y = c.STATS_Y
        y_offset = 60

        for i, (text, value, filename) in enumerate(lines):
            color = u.COLOR_GOLD
            if i == 0 and total_count < 22:  # Total count
                color = u.COLOR_RED
            elif i == 2:  # Special count
                color = u.COLOR_RED if special_count > 10 else u.COLOR_GREEN

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
        if self.carousel_scene:
            result = self.carousel_scene.handle_events(event)
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

        # Back button
        if self.back_button.check_click(event.pos):
            self.lock()
            self.save_user_deck()
            return self.back_button.action

        # Start button
        elif self.start_button.check_click(event.pos) and self.can_start_game():
            self.lock()
            self.save_user_deck()
            return self.start_button.action

        # Prev faction button
        elif self.prev_faction_button.check_click(event.pos):
            self.change_faction(direction=-1)

        # Next faction button
        elif self.next_faction_button.check_click(event.pos):
            self.change_faction(direction=1)

        # Commander selection
        elif self.commander_rect.collidepoint(event.pos):
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

    def change_faction(self, direction=0, faction=None):
        if faction:
            self.current_deck_index = self.factions.index(faction)
            direction = 0

        self.current_deck_index = (self.current_deck_index + direction) % len(self.factions)
        self.update_faction_buttons()

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
        total_count = unit_count = special_count = total_strength = hero_count = 0

        for card in deck.cards:
            count = card.count
            total_count += count

            if card.power is None:
                special_count += count
            elif card.is_card_type(CardType.UNIT):
                unit_count += count
                total_strength += card.power * count
            elif card.is_card_type(CardType.HERO):
                hero_count += count
                total_strength += card.power * count

        return total_count, unit_count, special_count, total_strength, hero_count

    def get_current_deck_dict(self):
        current_faction = self.get_faction()
        return self.all_decks[current_faction]

    def move_cards(self, origin, source, id, count):
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

    def move_to_left(self, id, count):
        self.move_cards("right", "left", id, count)

    def move_to_right(self, id, count):
        self.move_cards("left", "right", id, count)

    def can_start_game(self):
        total_count, _, special_count, _, _ = self.calculate_deck_stats()
        if total_count < 22 or special_count > 10:
            return False

        return True

    def close_carousel(self):
        self.carousel_scene = None

    def open_carousel(self):
        cards_data = db.get_faction_commanders(self.get_faction())
        commanders = [CommanderEntry(data) for data in cards_data]

        initial_index = 0
        current_commander_id = self.get_current_deck_dict()["commander"].id
        for i, commander in enumerate(commanders):
            if commander.id == current_commander_id:
                initial_index = i
                break

        self.carousel_scene = CarouselScene(self.screen, commanders, self.get_card_paths, initial_index=initial_index,
                                            choose_count=1, cancelable=True, label=False, opacity=0.75)

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
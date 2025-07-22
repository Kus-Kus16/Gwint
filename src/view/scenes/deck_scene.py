import pygame
from overrides import overrides

from src.model.card_holders.sorted_card_holder import SortedCardHolder
from src.model.cards import cards_database as db
from src.model.cards.card_entry import CardEntry
from src.model.cards.commander_entry import CommanderEntry
from src.model.enums.card_type import CardType
from src.model.enums.faction_type import FactionType
from src.view import constants as c, loader, saver
from src.view.components.button import Button
from src.view.constants import BUTTON_SIZE_WIDE
from src.view.scenes.carousel_scene import CarouselScene
from src.view.scenes.scene import Scene

CARD_MARGIN = 20
VISIBLE_CARDS = 6

ROWS = 2
COLS = 3
CARDS_PER_PAGE = ROWS * COLS

class DeckScene(Scene):
    def __init__(self, screen):
        super().__init__(screen)

        self.factions = [faction for faction in FactionType if faction != FactionType.NEUTRALNE]
        self.all_decks = {
            faction: {"left": SortedCardHolder(), "right": SortedCardHolder()}
            for faction in self.factions
        }

        userdata = loader.load_data("user_decks", is_userdata=True)
        self.current_deck_index = 0
        self.init_decks(userdata)

        self.carousel_scene = None

        # Click rects
        self.commander_rect = None
        self.left_card_rects = []
        self.right_card_rects = []

        # Buttons
        self.prev_faction_button = None
        self.next_faction_button = None

        button_width, button_height = c.BUTTON_SIZE_NARROW
        x, y = (self.screen_width - button_width) // 2, self.screen_height - button_height - 30
        self.back_button = Button("Menu",(x, y), c.BUTTON_SIZE_NARROW,
                                  {"type": "mode_change", "mode": "menu"})
        self.start_button = Button("Graj", (x, y - button_height - 10), c.BUTTON_SIZE_NARROW,
                                   {"type": "mode_change", "mode": "new_game", "load": True})
        self.update_faction_buttons()

        # Scroll
        self.scroll_offset_left = 0
        self.scroll_offset_right = 0

        self.dragging_scroll_left = False
        self.dragging_scroll_right = False
        self.scroll_start_left = None
        self.scroll_start_right = None
        self.drag_start_y = None
        self.scrollbar_width = 15

    def init_decks(self, userdata):
        for faction in self.factions:
            self.change_faction(faction=faction)
            decks = self.get_current_deck_dict()

            card_list = db.get_faction_cards(faction, include_neutral=True) #TODO add first commander
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

        self.prev_faction_button = Button(f"< {prev_name}", (50, 50), BUTTON_SIZE_WIDE,
                                          None, font=c.CINZEL_25_BOLD)
        self.next_faction_button = Button(f"{next_name} >", (self.screen_width - 450, 50), BUTTON_SIZE_WIDE,
                                          None, font=c.CINZEL_25_BOLD)

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
        self.draw_scrollbar()

        if self.carousel_scene:
            self.carousel_scene.draw()

    def draw_scrollbar(self):
        return

        # def draw_single_scrollbar(x, y, height, content_length, scroll_offset):
        #     if content_length > CARDS_PER_PAGE:
        #         proportion_visible = CARDS_PER_PAGE / content_length
        #         scrollbar_height = max(int(height * proportion_visible), 20)
        #         max_scroll = content_length - CARDS_PER_PAGE
        #         scrollbar_pos = int((height - scrollbar_height) * scroll_offset / max_scroll)
        #
        #         pygame.draw.rect(self.screen, c.COLOR_GOLD,
        #                          (x, y, self.scrollbar_width, height))
        #         pygame.draw.rect(self.screen, c.COLOR_BLACK,
        #                          (x, y + scrollbar_pos, self.scrollbar_width, scrollbar_height))
        # # LEFT
        # collection_x = 70 - self.scrollbar_width - 5
        # collection_y = 270
        # collection_height = ROWS * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN) - CARD_MARGIN
        # content_length_left = len(self.filtered_cards)
        # scroll_offset_left = self.scroll_offset_left
        #
        # draw_single_scrollbar(collection_x, collection_y, collection_height,
        #                            content_length_left, scroll_offset_left)
        #
        # # RIGHT
        # deck_x = self.screen_width - 70 + 5
        # deck_y = 270
        # deck_height = ROWS * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN) - CARD_MARGIN
        # content_length_right = len(self.get_deck_cards(self.current_deck_index))
        # scroll_offset_right = self.scroll_offset_right
        #
        # draw_single_scrollbar(deck_x, deck_y, deck_height,
        #                            content_length_right, scroll_offset_right)

    def draw_commander(self):
        commander = self.get_current_deck_dict().get("commander")
        if commander:
            x = (self.screen_width - c.MEDIUM_CARD_SIZE[0]) // 2
            y = 170
            self.commander_rect = self.draw_card(commander, x, y, "medium")

    def draw_buttons(self):
        mouse_pos = pygame.mouse.get_pos()
        self.prev_faction_button.draw(self.screen, mouse_pos)
        self.next_faction_button.draw(self.screen, mouse_pos)
        self.back_button.draw(self.screen, mouse_pos)
        self.start_button.draw(self.screen, mouse_pos)

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
        faction_name = FactionType.faction_to_fullname(self.get_faction())
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

    def draw_cards_pane(self, cards, rect_output, x_start, scroll_offset):
        rect_output.clear()

        visible_deck_cards = cards[scroll_offset:scroll_offset + CARDS_PER_PAGE]

        for idx, card in enumerate(visible_deck_cards):
            row = idx // COLS
            col = idx % COLS

            x = x_start + col * (c.MEDIUM_CARD_SIZE[0] + CARD_MARGIN)
            y = 270 + row * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN)

            rect = self.draw_card(card, x, y, "medium")
            rect_output.append((rect, card))

            if card.count > 1:
                overlay_x = x + c.MEDIUM_CARD_SIZE[0] - 60 - 10
                overlay_y = y + 10
                self.draw_label(card.count, overlay_x, overlay_y)

    def draw_left_cards(self):
        cards = self.get_current_deck_dict()["left"].cards
        self.draw_cards_pane(cards, self.left_card_rects, 70, self.scroll_offset_left)

    def draw_right_cards(self):
        cards = self.get_current_deck_dict()["right"].cards
        total_width = COLS * c.MEDIUM_CARD_SIZE[0] + (COLS - 1) * CARD_MARGIN
        x_start = self.screen_width - total_width - 70
        self.draw_cards_pane(cards, self.right_card_rects, x_start, self.scroll_offset_right)

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
                self.dragging_scroll_left = False
                self.dragging_scroll_right = False

        elif event.type == pygame.MOUSEMOTION:
            return self.handle_mousemotion(event)

    def handle_leftclick(self, event):
        mouse_x, mouse_y = event.pos

        # # Scrollbar
        # # Left
        # collection_x = 70 - self.scrollbar_width - 5
        # collection_y = 270
        # collection_height = ROWS * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN) - CARD_MARGIN
        # if (collection_x <= mouse_x <= collection_x + self.scrollbar_width) and (
        #      collection_y <= mouse_y <= collection_y + collection_height):
        #     self.dragging_scroll_left = True
        #     self.drag_start_y = mouse_y
        #     self.scroll_start_left = self.scroll_offset_left
        #     return
        #
        # # Right
        # deck_x = self.screen_width - 70 + 5
        # deck_y = 270
        # deck_height = ROWS * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN) - CARD_MARGIN
        # if (deck_x <= mouse_x <= deck_x + self.scrollbar_width) and (deck_y <= mouse_y <= deck_y + deck_height):
        #     self.dragging_scroll_right = True
        #     self.drag_start_y = mouse_y
        #     self.scroll_start_right = self.scroll_offset_right
        #     return

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
            cards = self.get_current_deck_dict()["left"].cards
            update_scroll_offset("scroll_offset_left", len(cards), event.button)
        else:
            cards = self.get_current_deck_dict()["right"].cards
            update_scroll_offset("scroll_offset_right", len(cards), event.button)

    def handle_mousemotion(self, event):
        return
        # def update_drag_scroll(dragging, drag_start_y, scroll_start, content_length, height, set_offset):
        #     if not dragging:
        #         return
        #
        #     max_scroll = max(0, content_length - CARDS_PER_PAGE)
        #     if max_scroll == 0:
        #         return
        #
        #     delta_y = event.pos[1] - drag_start_y
        #     visible_ratio = CARDS_PER_PAGE / content_length
        #     scrollbar_height = max(20, int(height * visible_ratio))
        #     scroll_range = height - scrollbar_height
        #     scroll_delta = int(delta_y * max_scroll / scroll_range)
        #     new_offset = scroll_start + scroll_delta
        #     set_offset(max(0, min(max_scroll, new_offset)))
        #
        # # Left scrollbar
        # update_drag_scroll(
        #     self.dragging_scroll_left,
        #     self.drag_start_y,
        #     self.scroll_start_left,
        #     len(self.filtered_cards),
        #     ROWS * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN) - CARD_MARGIN,
        #     lambda v: setattr(self, "scroll_offset_left", v)
        # )
        #
        # # Right scrollbar
        # update_drag_scroll(
        #     self.dragging_scroll_right,
        #     self.drag_start_y,
        #     self.scroll_start_right,
        #     len(self.get_deck_cards(self.current_deck_index)),
        #     ROWS * (c.MEDIUM_CARD_SIZE[1] + CARD_MARGIN) - CARD_MARGIN,
        #     lambda v: setattr(self, "scroll_offset_right", v)
        # )

    def change_faction(self, direction=0, faction=None):
        if faction:
            self.current_deck_index = self.factions.index(faction)
            direction = 0

        self.current_deck_index = (self.current_deck_index + direction) % len(self.factions)
        self.update_faction_buttons()
        self.scroll_offset_right = 0

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
        total_count = 0
        hero_count = 0
        special_count = 0
        total_strength = 0

        for card in deck.cards:
            count = card.count

            if card.is_card_type(CardType.HERO) or card.is_card_type(CardType.UNIT):
                total_count += count

            if card.is_card_type(CardType.HERO):
                hero_count += count
            if card.power is None:
                special_count += count
            else:
                total_strength += card.power * count

        return total_count, hero_count, special_count, total_strength

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
        total_count, hero_count, special_count, total_strength = self.calculate_deck_stats()
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
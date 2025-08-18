import pygame
from overrides import overrides

from src.model.enums.ability_type import AbilityType
from src.model.enums.card_type import CardType
from src.model.enums.cards_area import CardsArea
from src.model.enums.faction_type import FactionType
from src.model.enums.row_type import RowType
from src.view.constants import game_constants as c, ui_constants as u
from src.view.scenes.carousel_scene import CarouselScene
from src.view.scenes.choose_scene import ChooseScene
from src.view.scenes.endscreen import EndScreen
from src.view.scenes.scene import Scene


class GameScene(Scene):
    def __init__(self, screen):
        super().__init__(screen, "resources/board.jpg")
        self.game = None
        self.player_id = None
        self.selected_card = None

        self.hand_rects = []
        self.card_rects = []

    @overrides
    def handle_events(self, event):
        if self.temporary_drawable:
            return self.handle_temporary(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            return self.handle_right_click(event)

        if self.locked:
            return None

        result = self.handle_keydown_events(event)
        if result is not None:
            return result

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.handle_left_click(event)

    def handle_left_click(self, event):
        # Check hand clicks
        card = self.check_card_click(event, self.hand_rects)
        if card is not None:
            if not card.is_card_type(CardType.COMMANDER) or card.active:
                self.selected_card = card

            return None

        if self.selected_card is None:
            return None
        card = self.selected_card

        # Check row clicks
        if card.is_card_type(CardType.UNIT) or card.is_card_type(CardType.HERO):
            row_type = self.check_row_click(event, card.rows)
            if row_type is not None:
                return self.handle_row_clicks(card, row_type)

        # Check weather clicks
        if card.is_ability_type(AbilityType.WEATHER):
            if self.check_weather_click(event):
                self.lock()
                return {
                    "type": "play",
                    "card_id": card.id,
                    "row_type": RowType.ANY
                }

        # Check boosts clicks
        if card.is_ability_type(AbilityType.BOOST):
            row_type = self.check_boost_click(event, c.SELF_ROW_TYPES)
            if row_type is not None:
                self.lock()
                return {
                    "type": "play",
                    "card_id": card.id,
                    "row_type": row_type
                }

        # Check decoy
        if card.is_ability_type(AbilityType.TARGETING):
            target = self.check_card_click(event, self.card_rects)
            if target is None:
                return None

            row_type = self.check_row_click(event, c.SELF_ROW_TYPES)
            if row_type is not None:
                self.lock()
                return {
                    "type": "play",
                    "card_id": card.id,
                    "row_type": row_type,
                    "targets": [target.id],
                }

        # Check any board clicks
        if card.is_ability_type(AbilityType.ABSOLUTE):
            if self.check_board_click(event):
                self.lock()

                #Check commander
                if card.is_ability_type(AbilityType.CHOOSING):
                    return {
                        "type": "show_carousel",
                        "carousel": "choose",
                        "row_type": RowType.ANY,
                        "card": card
                    }

                return {
                    "type": "play",
                    "card_id": card.id,
                    "row_type": RowType.ANY
                }

    def handle_right_click(self, event):
        # Check row clicks
        row_type = self.check_row_click(event, c.ROW_TYPES)
        if row_type is not None:
            self.lock()
            return {
                "type": "show_carousel",
                "carousel": "zoom",
                "row_type": row_type
            }

        # Check weather clicks
        if self.check_weather_click(event):
            self.lock()
            return {
                "type": "show_carousel",
                "carousel": "zoom",
                "row_type": CardsArea.WEATHER
            }

        # Check grave clicks
        grave_type = self.check_grave_click(event)
        if grave_type is not None:
            self.lock()
            return {
                "type": "show_carousel",
                "carousel": "zoom",
                "row_type": grave_type
            }

        # Check commander clicks
        comm_type = self.check_commander_click(event)
        if comm_type is not None:
            self.lock()
            return {
                "type": "show_carousel",
                "carousel": "zoom",
                "row_type": comm_type
            }

    def handle_keydown_events(self, event):
        if event.type == pygame.KEYDOWN:
            #Pass
            if event.key == pygame.K_SPACE:
                self.lock()
                return {
                    "type": "play",
                    "card_id": None
                }

            if not self.selected_card or self.selected_card.is_card_type(CardType.COMMANDER):
                return None

            #Autoplay
            elif event.key == pygame.K_RETURN and len(self.selected_card.rows) > 0:
                self.lock()
                return {
                    "type": "play",
                    "card_id": self.selected_card.id,
                    "row_type": self.selected_card.rows[0]
                }

    def handle_row_clicks(self, card, row_type):
        self.lock()

        #Check medic
        if card.is_ability_type(AbilityType.CHOOSING):
            return {
                "type": "show_carousel",
                "carousel": "choose",
                "row_type": row_type,
                "card": card
            }

        return {
            "type": "play",
            "card_id": card.id,
            "row_type": row_type
        }

    @classmethod
    def check_card_click(cls, event, rect_container):
        for card, rect in rect_container:
            if rect.collidepoint(event.pos):
                return card

    @classmethod
    def check_row_click(cls, event, row_types):
        for row_type in row_types:
            row_rect = getattr(c, row_type.name)["UNIT_RECT"]
            if row_rect.collidepoint(event.pos):
                return row_type

    @classmethod
    def check_boost_click(cls, event, row_types):
        for row_type in row_types:
            boost_rect = getattr(c, row_type.name)["BOOST_RECT"]
            if boost_rect.collidepoint(event.pos):
                return row_type

    @classmethod
    def check_grave_click(cls, event):
        for grave_type, grave_rect in c.GRAVES:
            if grave_rect.collidepoint(event.pos):
                return grave_type

    @classmethod
    def check_commander_click(cls, event):
        for comm_type, comm_rect in c.COMMANDERS:
            if comm_rect.collidepoint(event.pos):
                return comm_type

    @classmethod
    def check_weather_click(cls, event):
        weather_rect = c.WEATHER_RECT
        return weather_rect.collidepoint(event.pos)

    @classmethod
    def check_board_click(cls, event):
        board_rect = c.BOARD_RECT
        return board_rect.collidepoint(event.pos)

    @overrides
    def draw(self):
        super().draw()

        self.draw_highlights()
        self.draw_rows()
        self.draw_hand()
        self.draw_weather()
        self.draw_selected()
        self.draw_players()
        self.draw_temporary()

    def draw_rows(self):
        self.card_rects.clear()
        rows = self.game.board.get_ordered_rows(self.player_id)
        row_types = c.ROW_TYPES

        for i, row in enumerate(rows):
            row_type = row_types[i]
            data = getattr(c, row_type.name)
            row_rect = data["UNIT_RECT"]
            boost_rect = data["BOOST_RECT"]
            text_x, text_y = data["TEXT_CENTER"]
            self.draw_row(row, row_rect, row_type)
            self.draw_row_boosts(row, boost_rect)
            self.draw_text(f"{row.points}", text_x, text_y, color=u.COLOR_BLACK, center=True, font=u.CINZEL_30_BOLD)

    def draw_players(self):
        self.draw_player(self.player_id, c.INFO_RECT)
        self.draw_player(1 - self.player_id, c.INFO_OPP_RECT, opponent=True)

        if self.game.current_player_id == self.player_id:
            x, y = c.INFO_POS
            overlay = pygame.Surface((308, 40), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))

            overlay_rect = overlay.get_rect(left=x + 126, bottom=y - 8)
            self.screen.blit(overlay, overlay_rect)

            centerx, centery = overlay_rect.center
            self.draw_text("Wciśnij spację aby spasować", centerx, centery, center=True,
                           color=u.COLOR_LIGHTGRAY, font=u.CINZEL_20_BOLD)

    def draw_player(self, player_id, info_rect, opponent=False):
        player = self.game.get_player(player_id)
        x, y = info_rect.topleft
        size = info_rect.size

        if self.game.current_player_id == player_id:
            pygame.draw.line(self.screen, u.COLOR_YELLOW, (info_rect.left, info_rect.top),
            (info_rect.right, info_rect.top), 3)
            pygame.draw.line(self.screen, u.COLOR_YELLOW, (info_rect.left, info_rect.bottom - 1),
            (info_rect.right, info_rect.bottom - 1), 3)

        overlay = pygame.Surface(size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (x, y))

        self.draw_icon("player_border", (116, 122), x + 60, y + 11)
        self.draw_icon("profile", (89, 90), x + 74, y + 30)
        self.draw_icon(f"tarcza_{player.faction.name.lower()}", (45, 50), x + 52, y + 12)
        self.draw_icon(f"total_{"opp" if opponent else "me"}", None, x + 427, y + 45)

        if self.game.get_round_result(player_id, include_abilities=False) == 1:
            self.draw_icon("high_score", None, x + 403, y + 40)

        if self.game.get_player(player_id).passed:
            self.draw_text("Pas", x + 453, y + 132, color=u.COLOR_WHITE, center=True, font=u.CINZEL_25_BOLD)

        self.draw_gems(player.hp, x, y)
        self.draw_icon("cards", None, x + 201, y + 88)
        self.draw_text(player.hand.size(), x + 257, y + 108, color=u.COLOR_GOLD, center=True)

        self.draw_text("Przeciwnik" if opponent else "Ty", x + 201, y + 12, color=u.COLOR_GOLD, font=u.CINZEL_20_BOLD)
        self.draw_text(FactionType.faction_to_fullname(player.faction), x + 201, y + 45, color=u.COLOR_LIGHTGRAY, font=u.CINZEL_15)

        points_pos = c.POINTS_OPP_POS if opponent else c.POINTS_POS
        self.draw_text(f"{player.points}", *points_pos, color=u.COLOR_BLACK, center=True, font=u.CINZEL_30_BOLD)

        filename = f"rewers_{player.faction.name.lower()}"
        self.draw_stack(player.deck, c.DECK_OPP_RECT if opponent else c.DECK_RECT,
                        image=self.load_ico_image(filename, u.DECK_CARD_SIZE), label=True)
        self.draw_stack(player.grave, c.GRAVE_OPP_RECT if opponent else c.GRAVE_RECT)

    def draw_stack(self, container, rect, image=None, label=False):
        card_size = image.get_rect().size if image is not None else u.SMALL_CARD_SIZE
        x, y = rect.centerx - card_size[0] // 2, rect.centery - card_size[1] // 2

        for card in container.cards:
            if image is None:
                self.draw_card(card, x, y, "small")
            else:
                rect = image.get_rect(topleft=(x, y))
                self.screen.blit(image, rect)
            x, y = x - 1, y - 1

        if label:
            overlay_x = rect.centerx - 30
            overlay_y = rect.bottom - 36
            self.draw_label(container.size(), overlay_x, overlay_y)

    def draw_gems(self, hp, x, y):
        gem_on = self.load_ico_image("gem_on")
        gem_off = self.load_ico_image("gem_off")
        self.screen.blit(gem_on if hp >= 2 else gem_off, (x + 306, y + 86))
        self.screen.blit(gem_on if hp >= 1 else gem_off, (x + 353, y + 86))

    def draw_row(self, row, row_rect, row_type):
        self.draw_card_holder(row.cards, row_rect, self.card_rects)
        if row.effects["weather"]:
            self.draw_icon(f"weather_{row_type.name.lower()}", None, row_rect.left - c.BOOST_ROW_SIZE[0], row_rect.top)

    def draw_row_boosts(self, row, boost_rect):
        cards = row.get_all_boosts_cards()
        self.draw_card_holder(cards, boost_rect, self.card_rects)

    def draw_hand(self):
        self.hand_rects.clear()
        hand = self.game.players[self.player_id].hand

        rect = c.HAND_RECT
        self.draw_card_holder(hand.cards, rect, self.hand_rects)
        self.draw_commanders(self.hand_rects)

    def draw_card_holder(self, cards, rect, card_rects_output):
        width = rect.width
        x, y = rect.left, rect.top
        count = len(cards)
        card_width = u.SMALL_CARD_SIZE[0]
        offset = card_width

        total_width = offset * (count - 1) #except last card (fully visible)
        if total_width > width - card_width:
            offset = offset * (width - card_width) / total_width

        for i, card in enumerate(cards):
            card_x = x + offset * i
            card_rect = self.draw_card(card, card_x, y, "small", highlight=card is self.selected_card)
            card_rects_output.append((card, card_rect))

    def draw_commanders(self, card_rect_output):
        commander_opp = self.game.get_player(1 - self.player_id).commander
        self.draw_commander(commander_opp, c.COMM_OPP_POS)
        commander = self.game.get_player(self.player_id).commander
        commander_rect = c.COMM_RECT
        self.draw_commander(commander, c.COMM_POS)
        card_rect_output.append((commander, commander_rect))

    def draw_commander(self, commander, pos):
        x, y = pos
        x_offset, y_offset = c.COMM_OFFSET
        self.draw_card(commander, x + x_offset, y + y_offset, "small", highlight=commander is self.selected_card)
        if not commander.active:
            overlay = pygame.Surface(c.COMM_SIZE, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, pos)
        else:
            self.draw_icon("leader", None, x + 120, y + 50)

    def draw_weather(self):
        weather = self.game.board.weather
        rect = c.WEATHER_RECT
        offset = c.WEATHER_OFFSET
        moved_rect = rect.move(offset)

        self.draw_card_holder(weather.cards, moved_rect, [])

    def draw_highlights(self):
        def make_surface(size):
            surface = pygame.Surface(size, pygame.SRCALPHA)
            surface.fill((*u.COLOR_HIGHLIGHT, u.ALPHA_HIGHLIGHT))
            return surface

        selected = self.selected_card
        if selected is None:
            return

        if selected.is_card_type(CardType.UNIT) or selected.is_card_type(CardType.HERO):
            surface = make_surface(c.UNIT_ROW_SIZE)

            for row_type in selected.rows:
                unit_rect = getattr(c, row_type.name)["UNIT_RECT"]
                self.screen.blit(surface, (unit_rect.x, unit_rect.y))
            return

        if selected.is_ability_type(AbilityType.WEATHER):
            rect = c.WEATHER_RECT
            surface = make_surface(rect.size)
            self.screen.blit(surface, (rect.x, rect.y))
            return

        if selected.is_ability_type(AbilityType.BOOST):
            surface = make_surface(c.BOOST_ROW_SIZE)
            for row_type in c.SELF_ROW_TYPES:
                boost_rect = getattr(c, row_type.name)["BOOST_RECT"]
                self.screen.blit(surface, (boost_rect.x, boost_rect.y))
            return

        if selected.is_ability_type(AbilityType.ABSOLUTE):
            board_rect = c.BOARD_RECT
            surface = make_surface(board_rect.size)
            self.screen.blit(surface, (board_rect.x, board_rect.y))
            return

    def draw_selected(self):
        if self.selected_card is None:
            return

        self.draw_card(self.selected_card, *c.SELECTED_CARD_POS, "large")

    def set_game(self, game, player_id):
        self.game = game
        self.player_id = player_id

    def deselect(self):
        self.selected_card = None

    # Debugging method
    def display_cursor_position(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        position_text = f"{mouse_x}, {mouse_y}, {self.player_id})"
        self.draw_text(position_text, 10, 10)

    def choose_first_player(self):
        self.lock()
        choose_screen = ChooseScene(self.screen)
        self.add_temporary(choose_screen)

    def end_game(self, result, round_history):
        self.lock()
        end_screen = EndScreen(self.screen, result, round_history)
        self.add_temporary(end_screen)

    @overrides
    def reset_all(self):
        self.reset()
        self.game = None
        self.player_id = None

    def reset(self):
        self.clear_temporary()
        self.selected_card = None
        self.selected_card = None

    @overrides
    def lock(self):
        drawable = self.get_first_handleable_drawable()
        if drawable:
            drawable.lock()
            return

        self.locked = True

    @overrides
    def unlock(self):
        drawable = self.get_first_handleable_drawable()
        if drawable:
            drawable.unlock()
            return

        self.locked = False

    def show_card_carousel(self, cards, choose_count, cancelable, label, redraw_label, allow_ending):
        carousel = CarouselScene(self.screen, cards, self.get_card_paths, choose_count,
            cancelable, allow_ending=allow_ending, label=label, redraw_label=redraw_label, opacity=0.5)
        self.add_temporary(carousel)

    def discard_temporary(self):
        self.pop_temporary()

    def set_card_carousel(self, cards):
        drawable = self.get_first_handleable_drawable()
        if drawable:
            drawable.set_cards(cards)
            return

    @overrides
    def get_card_paths(self, card, size):
        if size == "small" or card.faction != FactionType.NEUTRALNE:
            faction = card.faction
        else:
            faction = card.owner.faction

        faction = FactionType.faction_to_fullname(faction)
        filename = card.filename
        return faction, filename

import pygame
from overrides import overrides

from model import cards_database as db
from view import constants as c
from view.scenes.carousel_scene import CarouselScene
from view.scenes.endscreen import EndScreen
from view.scenes.scene import Scene


class GameScene(Scene):
    def __init__(self, screen, volume_slider):
        super().__init__(screen, "resources/board.jpg", volume_slider)
        self.game = None
        self.ended = False
        self.end_screen = None
        self.show_carousel = False
        self.carousel_scene = None
        self.player_id = None
        self.selected_card = None

        self.hand_rects = []
        self.card_rects = []

    @overrides
    def handle_events(self, event):
        self.volume_slider.handle_event(event)

        if self.ended:
            return self.end_screen.handle_events(event)

        if self.show_carousel:
            return self.carousel_scene.handle_events(event)

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
            if not card.is_commander() or card.active:
                self.selected_card = card

            return None

        if self.selected_card is None:
            return None
        card = self.selected_card

        # Check row clicks
        if card.is_unit() or card.is_hero():
            row_name = self.check_row_click(event, card.rows)
            if row_name is not None:
                return self.handle_row_clicks(card, row_name)

        # Check weather clicks
        if card.is_weather():
            if self.check_weather_click(event):
                self.lock()
                return {
                    "type": "play",
                    "card_id": card.id,
                    "row": "any"
                }

        # Check boosts clicks
        if card.is_boost():
            row_name = self.check_boost_click(event, c.SELF_ROW_NAMES)
            if row_name is not None:
                self.lock()
                return {
                    "type": "play",
                    "card_id": card.id,
                    "row": row_name
                }

        # Check decoy
        if card.is_targeting():
            target = self.check_card_click(event, self.card_rects)
            if target is None:
                return None

            row_name = self.check_row_click(event, c.SELF_ROW_NAMES)
            if row_name is not None:
                self.lock()
                return {
                    "type": "play",
                    "card_id": card.id,
                    "row": row_name,
                    "targets": [target.id],
                }

        # Check any board clicks
        if card.is_absolute():
            if self.check_board_click(event):
                self.lock()

                #Check commander
                if card.is_choosing():
                    return {
                        "type": "show_carousel",
                        "carousel": "choose",
                        "card_id": card.id,
                        "row": "any",
                        "ability": card.ability()
                    }

                return {
                    "type": "play",
                    "card_id": card.id,
                    "row": "any"
                }

    def handle_right_click(self, event):
        # Check row clicks
        row_name = self.check_row_click(event, c.ROW_NAMES)
        if row_name is not None:
            self.lock()
            return {
                "type": "show_carousel",
                "carousel": "zoom",
                "row": row_name
            }

        # Check weather clicks
        if self.check_weather_click(event):
            self.lock()
            return {
                "type": "show_carousel",
                "carousel": "zoom",
                "row": "WEATHER"
            }

        # Check grave clicks
        grave_name = self.check_grave_click(event)
        if grave_name is not None:
            self.lock()
            return {
                "type": "show_carousel",
                "carousel": "zoom",
                "row": grave_name
            }

        # Check commander clicks
        commander_name = self.check_commander_click(event)
        if commander_name is not None:
            self.lock()
            return {
                "type": "show_carousel",
                "carousel": "zoom",
                "row": commander_name
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

            if not self.selected_card or self.selected_card.is_commander():
                return None

            #Autoplay
            elif event.key == pygame.K_RETURN and len(self.selected_card.rows) > 0:
                self.lock()
                return {
                    "type": "play",
                    "card_id": self.selected_card.id,
                    "row": self.selected_card.rows[0]
                }

    def handle_row_clicks(self, card, row_name):
        self.lock()

        #Check medic
        if card.is_choosing():
            return {
                "type": "show_carousel",
                "carousel": "choose",
                "card_id": card.id,
                "row": row_name,
                "ability": "medic"
            }

        return {
            "type": "play",
            "card_id": card.id,
            "row": row_name
        }

    @classmethod
    def check_card_click(cls, event, rect_container):
        for card, rect in rect_container:
            if rect.collidepoint(event.pos):
                return card

    @classmethod
    def check_row_click(cls, event, row_names):
        for row_name in row_names:
            row_rect = getattr(c, row_name.upper())["UNIT_RECT"]
            if row_rect.collidepoint(event.pos):
                return row_name

    @classmethod
    def check_boost_click(cls, event, row_names):
        for row_name in row_names:
            boost_rect = getattr(c, row_name.upper())["BOOST_RECT"]
            if boost_rect.collidepoint(event.pos):
                return row_name

    @classmethod
    def check_grave_click(cls, event):
        for grave_name, grave_rect in c.GRAVES:
            if grave_rect.collidepoint(event.pos):
                return grave_name

    @classmethod
    def check_commander_click(cls, event):
        for comm_name, comm_rect in c.COMMANDERS:
            if comm_rect.collidepoint(event.pos):
                return comm_name

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

        # self.display_cursor_position()

        if self.ended and len(self.temporary_drawable) == 0:
            self.end_screen.draw()

        if self.show_carousel and len(self.temporary_drawable) == 0:
            self.carousel_scene.draw()

        self.volume_slider.draw(self.screen)

    def draw_rows(self):
        self.card_rects.clear()
        rows = self.game.board.get_ordered_rows(self.player_id)
        row_names = c.ROW_NAMES

        for i, row in enumerate(rows):
            row_name = row_names[i]
            data = getattr(c, row_name)
            row_rect = data["UNIT_RECT"]
            boost_rect = data["BOOST_RECT"]
            text_x, text_y = data["TEXT_CENTER"]
            self.draw_row(row, row_rect, row_name)
            self.draw_row_boosts(row, boost_rect)
            self.draw_text(f"{row.points}", text_x, text_y, color=c.COLOR_BLACK, center=True, font=c.CINZEL_30_BOLD)

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
                           color=c.COLOR_LIGHTGRAY, font=c.CINZEL_20_BOLD)

    def draw_player(self, player_id, info_rect, opponent=False):
        player = self.game.get_player(player_id)
        x, y = info_rect.topleft
        size = info_rect.size

        if self.game.current_player_id == player_id:
            pygame.draw.line(self.screen, c.COLOR_YELLOW, (info_rect.left, info_rect.top),
            (info_rect.right, info_rect.top), 3)
            pygame.draw.line(self.screen, c.COLOR_YELLOW, (info_rect.left, info_rect.bottom - 1),
            (info_rect.right, info_rect.bottom - 1), 3)

        overlay = pygame.Surface(size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (x, y))

        self.draw_icon("player_border", (116, 122), x + 60, y + 11)
        self.draw_icon("profile", (89, 90), x + 74, y + 30)
        self.draw_icon(f"tarcza_{db.faction_to_nickname(player.faction)}", (45, 50), x + 52, y + 12)
        self.draw_icon(f"total_{"opp" if opponent else "me"}", None, x + 427, y + 45)

        if self.game.is_winning_round(player_id):
            self.draw_icon("high_score", None, x + 403, y + 40)

        self.draw_gems(player.hp, x, y)
        self.draw_icon("cards", None, x + 201, y + 88)
        self.draw_text(player.hand.size(), x + 257, y + 108, color=c.COLOR_GOLD, center=True)

        self.draw_text("Przeciwnik" if opponent else "Ty", x + 201, y + 12, color=c.COLOR_GOLD, font=c.CINZEL_20_BOLD)
        self.draw_text(player.faction, x + 201, y + 45, color=c.COLOR_LIGHTGRAY, font=c.CINZEL_15)

        points_pos = c.POINTS_OPP_POS if opponent else c.POINTS_POS
        self.draw_text(f"{player.points}", *points_pos, color=c.COLOR_BLACK, center=True, font=c.CINZEL_30_BOLD)

        filename = f"rewers_{db.faction_to_nickname(player.faction)}"
        self.draw_stack(player.deck, c.DECK_OPP_RECT if opponent else c.DECK_RECT,
                        image=self.load_ico_image(filename, c.DECK_CARD_SIZE), label=True)
        self.draw_stack(player.grave, c.GRAVE_OPP_RECT if opponent else c.GRAVE_RECT)

    def draw_icon(self, filename, size, x, y):
        image = self.load_ico_image(filename, size)
        rect = image.get_rect(topleft=(x, y))
        self.screen.blit(image, rect)

    def draw_stack(self, container, rect, image=None, label=False):
        card_size = image.get_rect().size if image is not None else c.SMALL_CARD_SIZE
        x, y = rect.centerx - card_size[0] // 2, rect.centery - card_size[1] // 2

        for card in container.cards:
            if image is None:
                self.draw_card(card, x, y, "small")
            else:
                rect = image.get_rect(topleft=(x, y))
                self.screen.blit(image, rect)
            x, y = x - 1, y - 1

        if label:
            overlay = pygame.Surface((60, 36), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            overlay_x = rect.centerx - 30
            overlay_y = rect.bottom - 36
            self.screen.blit(overlay, (overlay_x, overlay_y))
            self.draw_text(container.size(), rect.centerx, rect.bottom - 18, center=True)

    def draw_gems(self, hp, x, y):
        gem_on = self.load_ico_image("gem_on")
        gem_off = self.load_ico_image("gem_off")
        self.screen.blit(gem_on if hp >= 2 else gem_off, (x + 306, y + 86))
        self.screen.blit(gem_on if hp >= 1 else gem_off, (x + 353, y + 86))

    def draw_row(self, row, row_rect, row_name):
        self.draw_card_holder(row.cards, row_rect, self.card_rects)
        if row.effects["weather"]:
            self.draw_icon(f"weather_{row_name.lower()}", None, row_rect.left - c.BOOST_ROW_SIZE[0], row_rect.top)

    def draw_row_boosts(self, row, boost_rect):
        cards = row.get_effect_cards()
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
        offset = 90

        total_width = offset * count

        if total_width > width:
            offset = offset * width / total_width

        for i, card in enumerate(cards):
            card_x = x + offset * i
            card_rect = self.draw_card(card, card_x - 4, y, "small", highlight=card is self.selected_card)
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
        self.draw_card(commander, *pos, "small", highlight=commander is self.selected_card)
        if not commander.active:
            overlay = pygame.Surface(c.COMM_SIZE, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200)) #20%
            self.screen.blit(overlay, pos)
        else:
            self.draw_icon("leader", None, x + 120, y + 50)

    def draw_weather(self):
        weather = self.game.board.weather
        rect = c.WEATHER_RECT
        x, y = rect.left, rect.top
        x_offset = 0
        y_offset = 11

        for card in weather.cards:
            self.draw_card(card, x + x_offset, y + y_offset, "small")
            x_offset += 90

    def draw_highlights(self):
        selected = self.selected_card

        if selected is None:
            return

        highlight_color = c.COLOR_HIGHLIGHT
        alpha = c.ALPHA_HIGHLIGHT

        if selected.is_unit() or selected.is_hero():
            rows = selected.rows
            rect_size = c.UNIT_ROW_SIZE

            surface = pygame.Surface(rect_size, pygame.SRCALPHA)
            surface.fill((*highlight_color, alpha))

            for row_name in rows:
                unit_rect = getattr(c, row_name.upper())["UNIT_RECT"]
                self.screen.blit(surface, (unit_rect.x, unit_rect.y))

            return

        if selected.is_weather():
            rect = c.WEATHER_RECT
            surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            surface.fill((*highlight_color, alpha))
            self.screen.blit(surface, (rect.x, rect.y))

            return

        if selected.is_boost():
            rect_size = c.BOOST_ROW_SIZE
            surface = pygame.Surface(rect_size, pygame.SRCALPHA)
            surface.fill((*highlight_color, alpha))

            rows = c.SELF_ROW_NAMES
            for row_name in rows:
                boost_rect = getattr(c, row_name)["BOOST_RECT"]
                self.screen.blit(surface, (boost_rect.x, boost_rect.y))

            return

        if selected.is_absolute():
            board_rect = c.BOARD_RECT
            surface = pygame.Surface(board_rect.size, pygame.SRCALPHA)
            surface.fill((*highlight_color, alpha))
            self.screen.blit(surface, (board_rect.x, board_rect.y))

            return

    def draw_selected(self):
        if self.selected_card is None:
            return

        self.draw_card(self.selected_card, *c.SELECTED_CARD_POS, "large")

    def draw_card(self, card, x, y, size, highlight=False):
        rect = super().draw_card(card, x, y, size, highlight)

        if size == "large":
            return rect

        if not card.is_commander() and not card.is_special() and not card.is_hero():
            if card.power > card.base_power:
                color = c.COLOR_GREEN
            elif card.power < card.base_power:
                color = c.COLOR_RED
            else:
                color = c.COLOR_BLACK

            font = c.MASON_30 if card.power < 10 else c.MASON_20
            self.draw_text(card.power, rect.x + 20, rect.y + 19, color=color, font=font, center=True)

        return rect

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

    def end_game(self, result, round_history):
        self.lock()
        self.end_screen = EndScreen(self.screen, result, round_history)
        self.ended = True

    @overrides
    def reset_all(self):
        self.reset()
        self.game = None
        self.player_id = None

    def reset(self):
        self.ended = False
        self.end_screen = None
        self.selected_card = None

    @overrides
    def lock(self):
        if self.end_screen is not None:
            self.end_screen.lock()
            return

        if self.carousel_scene is not None:
            self.carousel_scene.lock()
            return

        self.locked = True

    @overrides
    def unlock(self):
        if self.end_screen is not None:
            self.end_screen.unlock()
            return

        if self.carousel_scene is not None:
            self.carousel_scene.unlock()
            return

        self.locked = False

    def show_card_carousel(self, cards, choose_count, cancelable, label):
        self.carousel_scene = CarouselScene(
            self.screen,
            self.draw_card,
            cards,
            choose_count,
            cancelable,
            label
        )
        self.show_carousel = True

    def discard_card_carousel(self):
        self.show_carousel = False
        self.carousel_scene = None

    def set_card_carousel(self, cards):
        self.carousel_scene.set_cards(cards)

    @overrides
    def get_card_paths(self, card, size):
        if size == "small" or card.faction != "Neutralne":
            faction = card.faction
        else:
            faction = card.owner.faction

        filename = card.filename
        return faction, filename

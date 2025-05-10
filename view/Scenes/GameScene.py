import pygame
from overrides import overrides

from view import ImageLoader, Constants as C
from view.Scenes.Scene import Scene
from view.components.CarouselScene import CarouselScene
from view.components.EndScreen import EndScreen

def load_small_image(card):
    path = f"resources/small/{card.faction}/{card.filename}.png"
    return ImageLoader.load_image(path)

def load_large_image(card):
    faction = card.owner.faction if card.faction == "Neutralne" else card.faction
    path = f"resources/large/{faction}/{card.filename}.png"
    return ImageLoader.load_image(path)

def load_image(card, size):
    return load_small_image(card) if size == "small" else load_large_image(card)

class GameScene(Scene):
    def __init__(self, screen, framerate, font):
        super().__init__(screen, framerate, font, "resources/board.jpg")
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

        if self.locked:
            return None

        result = self.handle_keydown_events(event)
        if result is not None:
            return result

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.handle_left_click(event)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            return self.handle_right_click(event)

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
            row_name = self.check_boost_click(event, C.SELF_ROW_NAMES)
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

            row_name = self.check_row_click(event, C.SELF_ROW_NAMES)
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
        row_name = self.check_row_click(event, C.ROW_NAMES)
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
            row_rect = getattr(C, row_name.upper())["UNIT_RECT"]
            if row_rect.collidepoint(event.pos):
                return row_name

    @classmethod
    def check_boost_click(cls, event, row_names):
        for row_name in row_names:
            boost_rect = getattr(C, row_name.upper())["BOOST_RECT"]
            if boost_rect.collidepoint(event.pos):
                return row_name

    @classmethod
    def check_grave_click(cls, event):
        for grave_name, grave_rect in C.GRAVES:
            if grave_rect.collidepoint(event.pos):
                return grave_name

    @classmethod
    def check_commander_click(cls, event):
        for comm_name, comm_rect in C.COMMANDERS:
            if comm_rect.collidepoint(event.pos):
                return comm_name

    @classmethod
    def check_weather_click(cls, event):
        weather_rect = C.WEATHER_RECT
        return weather_rect.collidepoint(event.pos)

    @classmethod
    def check_board_click(cls, event):
        board_rect = C.BOARD_RECT
        return board_rect.collidepoint(event.pos)

    @overrides
    def draw(self):
        super().draw()

        self.draw_highlights()

        self.draw_rows()
        self.draw_hand()
        self.draw_weather()
        self.draw_selected()
        self.draw_stats()

        self.display_cursor_position()

        self.draw_temporary()

        if self.ended and len(self.temporary_drawable) == 0:
            self.end_screen.draw()

        if self.show_carousel:
            self.carousel_scene.draw()

        self.volume_slider.draw(self.screen)

    def draw_rows(self):
        self.card_rects.clear()
        rows = self.game.board.get_ordered_rows(self.player_id)
        row_names = C.ROW_NAMES

        for i, row in enumerate(rows):
            data = getattr(C, row_names[i])
            row_rect = data["UNIT_RECT"]
            text_x_center, text_y_center = data["TEXT_CENTER"]
            self.draw_row(row, row_rect)
            self.draw_text(f"{row.points}", text_x_center, text_y_center, color=C.COLOR_BLACK, center=True)

    def draw_stats(self):
        #PLAYER HP TEMPORARY
        self.draw_text(f"{self.game.players[self.player_id].hp}", x=400, y=715, color=(255, 255, 255))
        self.draw_text(f"{self.game.players[1 - self.player_id].hp}", x=400, y=312, color=(255, 255, 255))

        #Player points
        self.draw_text(f"{self.game.get_player(self.player_id).points}", *C.POINTS_POS, color=C.COLOR_BLACK, center=True)
        self.draw_text(f"{self.game.get_player(1 - self.player_id).points}", *C.POINTS_OPP_POS, color=C.COLOR_BLACK, center=True)

        #PLAYER GRAVE TEMPORARY
        self.draw_text(f"{self.game.players[self.player_id].grave.size()}", x=1550, y=900, color=(255, 255, 255))
        self.draw_text(f"{self.game.players[1 - self.player_id].grave.size()}", x=1550, y=150, color=(255, 255, 255))

        #PLAYER DECK TEMPORARY
        self.draw_text(f"{self.game.players[self.player_id].deck.size()}", x=1777, y=900, color=(255, 255, 255))
        self.draw_text(f"{self.game.players[1 - self.player_id].deck.size()}", x=1777, y=150, color=(255, 255, 255))

        #MOVE TEXT TEMPORARY
        if self.game.current_player_id == self.player_id:
            self.draw_text("Wciśnij spację by spasować", 570, 1000)
        else:
            self.draw_text("Oczekiwanie na ruch przeciwnika", 570, 1000)

    def draw_row(self, row, row_rect):
        self.draw_card_holder(row, row_rect, self.card_rects)

    def draw_hand(self):
        self.hand_rects.clear()
        hand = self.game.players[self.player_id].hand

        rect = C.HAND_RECT
        self.draw_card_holder(hand, rect, self.hand_rects)
        self.draw_commanders(self.hand_rects)

    def draw_card_holder(self, container, rect, card_rects_output):
        x, y = rect.left, rect.top
        offset = 0

        for card in container.cards:
            card_rect = self.draw_card(card, x + offset, y, "small")
            card_rects_output.append((card, card_rect))
            offset += 90

    def draw_commanders(self, card_rect_output):
        commander_opp = self.game.get_player(1 - self.player_id).commander
        self.draw_commander(commander_opp, C.COMM_OPP_POS)
        commander = self.game.get_player(self.player_id).commander
        commander_rect = C.COMM_RECT
        self.draw_commander(commander, C.COMM_POS)
        card_rect_output.append((commander, commander_rect))

    def draw_commander(self, commander, pos):
        self.draw_card(commander, *pos, "small")
        if not commander.active:
            overlay = pygame.Surface(C.COMM_SIZE, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200)) #20%
            self.screen.blit(overlay, pos)

    def draw_weather(self):
        weather = self.game.board.weather
        rect = C.WEATHER_RECT
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

        highlight_color = C.COLOR_HIGHLIGHT
        alpha = C.ALPHA_HIGHLIGHT

        if selected.is_unit() or selected.is_hero():
            rows = selected.rows
            rect_size = C.UNIT_ROW_SIZE

            surface = pygame.Surface(rect_size, pygame.SRCALPHA)
            surface.fill((*highlight_color, alpha))

            for row_name in rows:
                unit_rect = getattr(C, row_name.upper())["UNIT_RECT"]
                self.screen.blit(surface, (unit_rect.x, unit_rect.y))

            return

        if selected.is_weather():
            rect = C.WEATHER_RECT
            surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            surface.fill((*highlight_color, alpha))
            self.screen.blit(surface, (rect.x, rect.y))

            return

        if selected.is_boost():
            rect_size = C.BOOST_ROW_SIZE
            surface = pygame.Surface(rect_size, pygame.SRCALPHA)
            surface.fill((*highlight_color, alpha))

            rows = C.SELF_ROW_NAMES
            for row_name in rows:
                boost_rect = getattr(C, row_name)["BOOST_RECT"]
                self.screen.blit(surface, (boost_rect.x, boost_rect.y))

            return

        if selected.is_absolute():
            board_rect = C.BOARD_RECT
            surface = pygame.Surface(board_rect.size, pygame.SRCALPHA)
            surface.fill((*highlight_color, alpha))
            self.screen.blit(surface, (board_rect.x, board_rect.y))

            return

    def draw_selected(self):
        if self.selected_card is None:
            return

        self.draw_card(self.selected_card, *C.SELECTED_CARD_POS, "large")

    def draw_card(self, card, x, y, size):
        image = load_image(card, size)
        rect = image.get_rect(topleft=(x, y))
        self.screen.blit(image, rect)

        if size == "large":
            return rect

        if self.selected_card == card:
            pygame.draw.rect(self.screen, C.COLOR_YELLOW, rect, 4)

        if not card.is_commander() and not card.is_special() and not card.is_hero():
            if card.power > card.base_power:
                color = C.COLOR_GREEN
            elif card.power < card.base_power:
                color = C.COLOR_RED
            else:
                color = C.COLOR_BLACK

            self.draw_text(card.power, rect.x + 12, rect.y + 1, color=color)

        return rect

    def draw_text(self, text, x, y, color=C.COLOR_WHITE, center=False):
        text_surface = self.font.render(str(text), True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)

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
        self.end_screen = EndScreen(self.screen, result, round_history, self.framerate, self.font)
        self.ended = True

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

    def show_card_carousel(self, cards, choose_count, cancelable):
        self.carousel_scene = CarouselScene(
            self.screen,
            self.framerate,
            self.font,
            self.draw_card,
            cards,
            choose_count,
            cancelable
        )
        self.show_carousel = True

    def discard_card_carousel(self):
        self.show_carousel = False
        self.carousel_scene = None
import pygame
from overrides import overrides

from view import ImageLoader
from view.Scenes.Scene import Scene
from view.components.EndScreen import EndScreen


def load_image(card, size):
    path = f"resources/{size}/{card.faction}/{card.filename}.png"
    return ImageLoader.load_image(path)

def load_small_image(card):
    return load_image(card, "small")

def load_large_image(card):
    return load_image(card, "large")

class GameScene(Scene):
    def __init__(self, screen, framerate, font):
        super().__init__(screen, framerate, font, "resources/board.jpg")
        self.game = None
        self.ended = False
        self.end_screen = None
        self.player_id = None
        self.selected_card = None
        self.zoomed_card = None #TODO

        self.hand_rects = []
        self.card_rects = []

        self.consts = {}
        self.init_consts()

    @overrides
    def handle_events(self, event):
        self.volume_slider.handle_event(event)

        if self.ended:
            return self.end_screen.handle_events(event)

        if self.locked:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.lock()
                return {
                    "type": "play",
                    "card_id": None
                }

            elif event.key == pygame.K_RETURN and self.selected_card and len(self.selected_card.rows) > 0:
                #TODO nie dziala ze specjalnymi
                self.lock()
                return {
                    "type": "play",
                    "card_id": self.selected_card.id,
                    "row": self.selected_card.rows[0]
                }

        elif event.type == pygame.MOUSEBUTTONDOWN:
                #Check hand clicks
                for card, rect in self.hand_rects:
                    if rect.collidepoint(event.pos):
                        self.selected_card = card
                        return None

                if self.selected_card is None:
                    return None

                card = self.selected_card

                #Check row clicks
                if card.is_unit() or card.is_hero():
                    row_names = card.rows

                    for row_name in row_names:
                        row_rect = self.consts[row_name]["unit_rect"]
                        if row_rect.collidepoint(event.pos):
                            self.lock()
                            return {
                                "type": "play",
                                "card_id": card.id,
                                "row": row_name
                            }

                #Check weather clicks
                if card.is_weather():
                    weather_rect = self.consts["weather"]["rect"]

                    if weather_rect.collidepoint(event.pos):
                        self.lock()
                        return {
                            "type": "play",
                            "card_id": card.id,
                            "row": "any"
                        }

                #Check boosts clicks
                if card.is_boost():
                    row_names = ["close", "ranged", "siege"]
                    for row_name in row_names:
                        boost_rect = self.consts[row_name]["boost_rect"]
                        if boost_rect.collidepoint(event.pos):
                            self.lock()
                            return {
                                "type": "play",
                                "card_id": card.id,
                                "row": row_name
                            }

                #Check decoy
                if card.is_targeting():
                    target = None
                    for target_card, target_rect in self.card_rects:
                        if target_rect.collidepoint(event.pos):
                            target = target_card
                            break

                    if target is None:
                        return None

                    row_names = self.consts["row_names"]
                    for row_name in row_names:
                        row_rect = self.consts[row_name]["unit_rect"]
                        if row_rect.collidepoint(event.pos):
                            self.lock()
                            return {
                                "type": "play",
                                "card_id": card.id,
                                "row": row_name,
                                "targets": [target], #TODO ended here
                            }

                #Check any board clicks
                if card.is_absolute():
                    board_rect = self.consts["board"]["rect"]

                    if board_rect.collidepoint(event.pos):
                        self.lock()
                        return {
                            "type": "play",
                            "card_id": card.id,
                            "row": "any"
                        }

    @overrides
    def draw(self):
        super().draw()

        self.draw_highlights()

        self.draw_rows()
        self.draw_hand()
        self.draw_weather()
        self.draw_stats()

        self.display_cursor_position()

        self.draw_temporary()

        if self.ended and len(self.temporary_drawable) == 0:
            self.end_screen.draw()

        self.volume_slider.draw(self.screen)

    def draw_rows(self):
        self.card_rects.clear()
        rows = self.game.board.get_ordered_rows(self.player_id)
        row_names = self.consts["row_names"]

        for i, row in enumerate(rows):
            data = self.consts[row_names[i]]
            row_rect = data["unit_rect"]
            text_x_center, text_y_center = data["text_center"]
            self.draw_row(row, row_rect)
            self.draw_text(f"{row.points}", text_x_center, text_y_center, color=(0, 0, 0), center=True)

    def draw_stats(self):
        #PLAYER HP
        self.draw_text(f"{self.game.players[self.player_id].hp}", x=400, y=715, color=(255, 255, 255))
        self.draw_text(f"{self.game.players[1 - self.player_id].hp}", x=400, y=312, color=(255, 255, 255))

        #PLAYER POINTS
        self.draw_text(f"{self.game.players[self.player_id].points}", x=453, y=734,color=(0,0,0), center=True)
        self.draw_text(f"{self.game.players[1 - self.player_id].points}", x=453, y=332,color=(0,0,0), center=True)

        #PLAYER GRAVE
        self.draw_text(f"{self.game.players[self.player_id].grave.size()}", x=1550, y=900, color=(255, 255, 255))
        self.draw_text(f"{self.game.players[1 - self.player_id].grave.size()}", x=1550, y=150, color=(255, 255, 255))

        #PLAYER DECK
        self.draw_text(f"{self.game.players[self.player_id].deck.size()}", x=1777, y=900, color=(255, 255, 255))
        self.draw_text(f"{self.game.players[1 - self.player_id].deck.size()}", x=1777, y=150, color=(255, 255, 255))

        #MOVE TEXT
        if self.game.current_player_id == self.player_id:
            self.draw_text("Wciśnij spację by spasować", 570, 1000)
        else:
            self.draw_text("Oczekiwanie na ruch przeciwnika", 570, 1000)

    def draw_row(self, row, row_rect):
        self.draw_card_holder(row, row_rect, self.card_rects)

    def draw_hand(self):
        self.hand_rects.clear()
        hand = self.game.players[self.player_id].hand

        rect = self.consts["hand"]["rect"]
        self.draw_card_holder(hand, rect, self.hand_rects)

    def draw_card_holder(self, container, rect, card_rects_output):
        x, y = rect.left, rect.top
        offset = 0

        for card in container:
            card_rect = self.draw_card(card, x + offset, y, "small")
            card_rects_output.append((card, card_rect))
            offset += 90

    def draw_weather(self):
        weather = self.game.board.weather

        rect = self.consts["weather"]["rect"]
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

        highlight_color = (255, 255, 0)
        alpha = 50

        if selected.is_unit() or selected.is_hero():
            rows = selected.rows
            rect_size = self.consts["unit_row_size"]

            surface = pygame.Surface(rect_size, pygame.SRCALPHA)
            surface.fill((*highlight_color, alpha))

            for row_name in rows:
                unit_rect = self.consts[row_name]["unit_rect"]
                self.screen.blit(surface, (unit_rect.x, unit_rect.y))

            return

        if selected.is_weather():
            rect = self.consts["weather"]["rect"]
            surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            surface.fill((*highlight_color, alpha))
            self.screen.blit(surface, (rect.x, rect.y))

            return

        if selected.is_special():
            rect_size = self.consts["boost_row_size"]
            surface = pygame.Surface(rect_size, pygame.SRCALPHA)
            surface.fill((*highlight_color, alpha))

            rows = ["close", "ranged", "siege"]
            for row_name in rows:
                boost_rect = self.consts[row_name]["boost_rect"]
                self.screen.blit(surface, (boost_rect.x, boost_rect.y))

            return

    def draw_card(self, card, x, y, size):
        image = load_image(card, size)
        rect = image.get_rect(topleft=(x, y))
        self.screen.blit(image, rect)

        if self.selected_card == card:
            pygame.draw.rect(self.screen, (212, 175, 55), rect, 4)

        if not card.is_special() and not card.is_hero():
            if card.power > card.base_power:
                color = (20, 140, 60)
            elif card.power < card.base_power:
                color = (237, 56, 24)
            else:
                color = (0, 0, 0)

            self.draw_text(card.power, rect.x + 12, rect.y + 1, color=color)

        return rect

    def draw_text(self, text, x, y, color=(255, 255, 255), center=False):
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

    def init_consts(self):
        positions_y = {
            # name, (row_y, text_y_center)
            "siege_OPP": (17, 74),
            "ranged_OPP": (149, 205),
            "close_OPP": (286, 343),
            "close": (435, 492),
            "ranged": (567, 625),
            "siege": (705, 763)
        }

        unit_x = 707
        boost_x = 570
        text_x_center = 536
        unit_size = (812, 119)
        boost_size = (130, 119)

        weather_pos = (140, 448)
        weather_size = (281, 140)
        hand_pos = (577, 842)
        hand_size = (936, 125)
        board_pos = (570, 17)
        board_size = (949, 807)

        consts = {
            "row_names": [],
            "unit_row_size": unit_size,
            "boost_row_size": boost_size
        }

        for row_name, (row_y, text_y_center) in positions_y.items():
            unit_rect = pygame.Rect(unit_x, row_y, *unit_size)
            boost_rect = pygame.Rect(boost_x, row_y, *boost_size)
            consts[row_name] = { "unit_rect": unit_rect, "boost_rect": boost_rect, "text_center": (text_x_center, text_y_center) }
            consts["row_names"].append(row_name)

        weather_rect = pygame.Rect(*weather_pos, *weather_size)
        consts["weather"] = { "rect": weather_rect }

        hand_rect = pygame.Rect(*hand_pos, *hand_size)
        consts["hand"] = { "rect": hand_rect }

        board_rect = pygame.Rect(*board_pos, *board_size)
        consts["board"] = {"rect": board_rect}

        self.consts = consts

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
        self.zoomed_card = None

    @overrides
    def lock(self):
        if self.end_screen is not None:
            self.end_screen.lock()
            return

        self.locked = True

    @overrides
    def unlock(self):
        if self.end_screen is not None:
            self.end_screen.unlock()
            return

        self.locked = False
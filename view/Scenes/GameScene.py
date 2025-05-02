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

        self.hand_rects = [] #TODO To be changed - all "card images" need a saved rect for zoom
        self.row_rects = []

        self.init_row_rects()

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

                #Check row clics #TODO Other clicks
                if self.selected_card is not None:
                    for row_name, unit_rect, _, _ in self.row_rects:
                        if unit_rect.collidepoint(event.pos):
                            self.lock()
                            return {
                                "type": "play",
                                "card_id": self.selected_card.id,
                                "row": row_name
                            }

    @overrides
    def draw(self):
        super().draw()

        self.draw_rows()
        self.draw_hand()
        self.draw_stats()

        self.draw_highlights()
        self.display_cursor_position()

        self.draw_temporary()

        if self.ended and len(self.temporary_drawable) == 0:
            self.end_screen.draw()

        self.volume_slider.draw(self.screen)

    def draw_rows(self):
        rows = self.game.board.get_ordered_rows(self.player_id)
        positions = self.row_rects

        for i, row in enumerate(rows):
            unit_rect, (text_x_center, text_y_center) = positions[i][1], positions[i][3]
            unit_x, unit_y = unit_rect.left, unit_rect.top
            self.draw_row(row, unit_x, unit_y)
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

    def draw_row(self, row, x, y):
        offset = 0
        for card in row.cards:
            self.draw_card(card, x + offset, y, "small")
            offset += 90

    def draw_hand(self):
        self.hand_rects.clear()
        hand = self.game.players[self.player_id].hand

        x = 585
        y = 845
        offset = 0

        for card in hand.cards:
            rect = self.draw_card(card, x + offset, y, "small")
            self.hand_rects.append((card, rect))
            offset += 90

    def draw_highlights(self):
        if self.selected_card is None:
            return

        rows = self.selected_card.rows
        # rows = ["close", "ranged", "siege", "close_OPP", "ranged_OPP", "siege_OPP"]
        highlight_color = (255, 255, 0)
        alpha = 50

        surface = pygame.Surface((812, 119), pygame.SRCALPHA)
        surface.fill((*highlight_color, alpha))

        for row_name in rows:
            unit_rect = self.get_row_rects(row_name)[1]
            self.screen.blit(surface, (unit_rect.x, unit_rect.y))

    def draw_card(self, card, x, y, size):
        image = load_image(card, size)
        rect = image.get_rect(topleft=(x, y))
        self.screen.blit(image, rect)

        if self.selected_card == card:
            pygame.draw.rect(self.screen, (212, 175, 55), rect, 4)

        if not card.is_special() and not card.is_hero():
            self.draw_text(card.power, rect.x + 12, rect.y + 1, color=(0, 0, 0))

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

    def init_row_rects(self):
        positions_y = {
            # name, (row_y, text_y_center)
            "siege_OPP": (17, 74),
            "ranged_OPP": (149, 205),
            "close_OPP": (286, 343),
            "close": (435, 492),
            "ranged": (567, 625),
            "siege": (705, 763)
        }

        unit_size, unit_x = (812, 119), 700
        boost_size, boost_x = (130, 119), 570
        text_x_center = 536

        for row_name, (row_y, text_y_center) in positions_y.items():
            unit_rect = pygame.Rect(unit_x, row_y, *unit_size)
            boost_rect = pygame.Rect(boost_x, row_y, *boost_size)
            self.row_rects.append( (row_name, unit_rect, boost_rect, (text_x_center, text_y_center)) )

    def get_row_rects(self, name):
        for row_rect in self.row_rects:
            row_name = row_rect[0]
            if row_name == name:
                return row_rect

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
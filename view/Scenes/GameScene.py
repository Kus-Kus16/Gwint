import os
import pygame
from overrides import overrides

from view import ImageLoader
from view.Scenes.Scene import Scene

def load_image(card, size):
    path = f"resources/{size}/{card.faction}/{card.filename}.png"
    return ImageLoader.load_image(path)

def load_small_image(card):
    return load_image(card, "small")

def load_large_image(card):
    return load_image(card, "large")

class GameScene(Scene):
    def __init__(self, screen, font):
        super().__init__(screen, font, "resources/board.jpg")
        self.game = None
        self.player_id = None
        self.selected_card = None
        self.zoomed_card = None #TODO

        self.hand_rects = [] #TODO To be changed - all "card images" need a saved rect for zoom
        self.row_rects = []

        self.init_row_rects()

    @overrides
    def handle_events(self, event):
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

                #Check row clics
                if self.selected_card is not None:
                    for row_name, rect in self.row_rects:
                        if rect.collidepoint(event.pos):
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

        self.draw_row_highlights()
        self.display_cursor_position()

        self.draw_temporary()

    def draw_rows(self):
        rows = self.game.board.get_ordered_rows(self.player_id)
        positions = self.row_rects

        for i, row in enumerate(rows):
            y = positions[i][1].top
            self.draw_row(row, 720, y)
            self.draw_text(f"{row.points}", 528, y + 44, color=(0, 0, 0))

    def draw_stats(self):
        #PLAYER HP
        self.draw_text(f"{self.game.players[self.player_id].hp}", x=400, y=715, color=(255, 255, 255))
        self.draw_text(f"{self.game.players[1 - self.player_id].hp}", x=400, y=312, color=(255, 255, 255))

        #PLAYER POINTS
        self.draw_text(f"{self.game.players[self.player_id].points}", x=445, y=715,color=(0,0,0))
        self.draw_text(f"{self.game.players[1 - self.player_id].points}", x=445, y=312,color=(0,0,0))

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

    def draw_row_highlights(self):
        if self.selected_card is None:
            return

        rows = self.selected_card.rows
        highlight_color = (255, 255, 0)
        alpha = 50

        surface = pygame.Surface((815, 113), pygame.SRCALPHA)
        surface.fill((*highlight_color, alpha))

        for row_name in rows:
            rect = self.get_row_rect(row_name)
            self.screen.blit(surface, (rect.x, rect.y))

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
        positions = {
            "siege_OPP": 13,
            "ranged_OPP": 145,
            "close_OPP": 275,
            "close": 431,
            "ranged": 562,
            "siege": 700
        }

        for row_name, y in positions.items():
            rect = pygame.Rect(708, y + 10, 815, 113)
            self.row_rects.append((row_name, rect))

    def get_row_rect(self, name):
        for row_name, rect in self.row_rects:
            if row_name == name:
                return rect

    def deselect(self):
        self.selected_card = None

    # Debugging method
    def display_cursor_position(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        position_text = f"{mouse_x}, {mouse_y}, {self.player_id})"
        self.draw_text(position_text, 10, 10)
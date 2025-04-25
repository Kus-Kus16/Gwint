import os
import pygame


def load_small_image(card):
    path = f"resources/small/{card.faction}/{card.filename}.png"
    if os.path.exists(path):
        return pygame.image.load(path).convert_alpha()
    else:
        print(f"[WARN] Brak pliku: {path}")
        return pygame.image.load("resources/placeholder.png").convert_alpha()

def load_large_image(card):
    path = f"resources/large/{card.faction}/{card.filename}.png"
    if os.path.exists(path):
        return pygame.image.load(path).convert_alpha()
    else:
        print(f"[WARN] Brak pliku: {path}")
        return pygame.image.load("resources/placeholder.png").convert_alpha()


class GameScene:
    def __init__(self, screen, font, application_status):
        self.screen = screen
        self.font = font
        self.screen_width, self.screen_height = screen.get_size()
        self.application_status = application_status
        self.game = None
        self.player_id = None
        self.selected_card = None
        self.hand_rects = None

        self.background = pygame.image.load("resources/board.jpg").convert()
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))

        self.row_highlight_rects = []

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        row = self.game.board.rows
        row_points = [row.points for row in self.game.board.rows]
        if self.player_id%2==1:
            self.draw_row(row[2], x=720, y=13)
            self.draw_row(row[1], x=720, y=145)
            self.draw_row(row[0], x=720, y=275)
            self.draw_row(row[3], x=720, y=431)
            self.draw_row(row[4], x=720, y=562)
            self.draw_row(row[5], x=720, y=700)

            self.draw_text(f"{row_points[2]}", x=528, y=56, color=(0, 0, 0))
            self.draw_text(f"{row_points[1]}", x=528, y=186, color=(0, 0, 0))
            self.draw_text(f"{row_points[0]}", x=528, y=323, color=(0, 0, 0))
            self.draw_text(f"{row_points[3]}", x=528, y=471, color=(0, 0, 0))
            self.draw_text(f"{row_points[4]}", x=528, y=606, color=(0, 0, 0))
            self.draw_text(f"{row_points[5]}", x=528, y=744, color=(0, 0, 0))
        else:
            self.draw_row(row[5], x=720, y=13)
            self.draw_row(row[4], x=720, y=145)
            self.draw_row(row[3], x=720, y=270)
            self.draw_row(row[0], x=720, y=431)
            self.draw_row(row[1], x=720, y=562)
            self.draw_row(row[2], x=720, y=700)

            self.draw_text(f"{row_points[5]}", x=528, y=56, color=(0, 0, 0))
            self.draw_text(f"{row_points[4]}", x=528, y=186, color=(0, 0, 0))
            self.draw_text(f"{row_points[3]}", x=528, y=323, color=(0, 0, 0))
            self.draw_text(f"{row_points[0]}", x=528, y=471, color=(0, 0, 0))
            self.draw_text(f"{row_points[1]}", x=528, y=606, color=(0, 0, 0))
            self.draw_text(f"{row_points[2]}", x=528, y=744, color=(0, 0, 0))

        hand = self.game.players[self.player_id].hand
        self.draw_hand(hand.cards, x=585, y=845)

        #PLAYER HP
        self.draw_text(f"{self.game.players[self.player_id].hp}", x=400, y=715, color=(255, 255, 255))
        self.draw_text(f"{self.game.players[self.player_id-1].hp}", x=400, y=312, color=(255, 255, 255))

        #PLAYER POINTS
        self.draw_text(f"{self.game.players[self.player_id].points}", x=445, y=715,color=(0,0,0))
        self.draw_text(f"{self.game.players[self.player_id-1].points}", x=445, y=312,color=(0,0,0))



    def draw_waiting(self):
        self.draw()
        self.draw_text("Oczekiwanie na ruch przeciwnika",570, 1000)

    def draw_playing(self):
        self.draw()
        self.draw_text("Wciśnij spację by spasować",570, 1000)

        if self.selected_card:
            self.draw_row_highlights(self.selected_card.rows)

    def display_cursor_position(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        position_text = f"{mouse_x}, {mouse_y})"
        self.draw_text(position_text, 10, 10)


    def draw_text(self, text, x, y, color=(255, 255, 255), center=False):
        text_surface = self.font.render(str(text), True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_row(self, row, x, y):
        offset = 0
        for card in row.cards:
            image = load_small_image(card)
            rect = image.get_rect(topleft=(x + offset, y))
            self.screen.blit(image, (x + offset, y))
            offset += 90

            if not card.is_special() and not card.is_hero():
                self.draw_text(card.power, rect.x + 12, rect.y + 1, color=(0, 0, 0))

    def draw_hand(self, hand_cards, x, y):
        offset = 0
        self.hand_rects = []

        for card in hand_cards:
            image = load_small_image(card)
            rect = image.get_rect(topleft=(x + offset, y))
            self.screen.blit(image, rect)

            if self.selected_card == card:
                pygame.draw.rect(self.screen, 	(212, 175, 55), rect, 4) #OBWÓDKA

            if not card.is_special() and not card.is_hero():
                self.draw_text(card.power, rect.x + 11, rect.y + 2, color=(0, 0, 0))

            self.hand_rects.append((card, rect))
            offset += 90

    def draw_row_highlights(self, rows):
        self.row_highlight_rects = []
        highlight_color = (255, 255, 0)
        alpha = 100

        surface = pygame.Surface((815, 113), pygame.SRCALPHA)
        surface.fill((*highlight_color, alpha))

        positions = {
            "close": 431,
            "ranged": 562,
            "siege": 700
        }

        for row_name in rows:
            y = positions[row_name]
            rect = pygame.Rect(708, y+10, 815, 113)
            self.screen.blit(surface, (rect.x, rect.y))
            self.row_highlight_rects.append((row_name, rect))

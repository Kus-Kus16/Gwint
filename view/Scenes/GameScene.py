import os

import pygame


class GameScene:
    def __init__(self, screen, font, game, player_id, application_status):
        self.screen = screen
        self.font = font
        self.screen_width, self.screen_height = screen.get_size()
        self.application_status = application_status
        self.game = game
        self.player_id = player_id

        self.background = pygame.image.load("resources/board.jpg").convert()
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        row = self.game.board.rows[0]
        #self.draw_hand(row, x=100, y=300)

        hand = self.game.players[self.player_id].hand
        #self.draw_hand(hand.cards, x=585, y=845)

        row_points = [row.points for row in self.game.board.rows]
        self.draw_text(f"{row_points[0]}", x=528, y=56,color=(0,0,0))
        self.draw_text(f"{row_points[1]}", x=528, y=186,color=(0,0,0))
        self.draw_text(f"{row_points[2]}", x=528, y=323,color=(0,0,0))
        self.draw_text(f"{row_points[3]}", x=528, y=471,color=(0,0,0))
        self.draw_text(f"{row_points[4]}", x=528, y=606,color=(0,0,0))
        self.draw_text(f"{row_points[5]}", x=528, y=744,color=(0,0,0))

        self.draw_text(f"{self.game.players[self.player_id].points}", x=445, y=715,color=(0,0,0))
        self.draw_text(f"{self.game.players[self.player_id-1].points}", x=445, y=312,color=(0,0,0))

        self.display_cursor_position()


    def draw_waiting(self):
        self.draw()
        self.draw_text("Oczekiwanie na ruch przeciwnika",570, 1000)

    def draw_playing(self):
        self.draw()
        self.draw_text("Wciśnij spację by spasować",570, 1000)

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

    def load_card_image(self,card):
        path = f"resources/small/{card.faction}/{card.filename}.png"
        if os.path.exists(path):
            return pygame.image.load(path).convert_alpha()
        else:
            print(f"[WARN] Brak pliku: {path}")
            return pygame.image.load("resources/placeholder.png").convert_alpha()


    def draw_row(self, row, x, y):
        offset = 0
        for card in row.cards:
            image = self.load_card_image(card)
            image = pygame.transform.scale(image, (80, 120))
            self.screen.blit(image, (x + offset, y))
            offset += 90

            image = pygame.transform.scale(image, (80, 120))
            self.screen.blit(image, (x + offset, y))
            offset += 90


import pygame


class PygameView:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Gwent LAN")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.running = True
        self.mode = "menu"
        self.pending_event = None
        self.selected_card = None
        self.locked = False
        self.game = None
        self.player_id = 0

    def run(self):
        while self.running:
            self.handle_pygame_events()
            match self.mode:
                case "menu":
                    self.show_menu()
                case "deck":
                    pass
                case "game":
                    self.show_game(self.game, self.player_id)
            self.clock.tick(60)

    def show_game(self, game, player_id):
        self.screen.fill((30, 30, 30))
        self.draw_text(f"Twój przeciwnik: {game.players[1 - player_id]}", 50, 50)
        pygame.display.flip()

    def set_game_state(self, game, player_id):
        self.game = game
        self.player_id = player_id

    def handle_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                card = self.get_card_under_mouse()
                if card:
                    self.selected_card = card

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.selected_card:
                    self.locked = True
                    row = self.selected_card.rows[0]
                    self.pending_event = {
                        "type": "card",
                        "card_id": self.selected_card.id,
                        "row": row
                    }

    def unlock(self):
        self.locked = False

    def get_event(self):
        result = self.pending_event
        self.pending_event = None
        return result

    def get_clicked_card(self):
        pass

    def show_error(self, error):
        print(error)

import pygame

from view.Scenes.CreditsScene import CreditsScene
from view.Scenes.MenuScene import MenuScene


class PygameView:
    def __init__(self):
        pygame.init()
        #self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        #self.screen = pygame.display.set_mode((1000,500))
        #self.screen = pygame.display.set_mode((1800,1000))
        #self.screen = pygame.display.set_mode((1280, 720))

        info = pygame.display.Info()
        self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN | pygame.SCALED)

        pygame.display.set_caption("Gwent LAN")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("resources/Cinzel/Cinzel-VariableFont_wght.ttf", 30)
        self.running = True
        self.mode = "menu"
        self.pending_event = None
        self.selected_card = None
        self.locked = False
        self.game = None
        self.player_id = 0

        self.screen_width, self.screen_height = self.screen.get_size()

        # Soundtrack
        pygame.mixer.init()
        pygame.mixer.music.load("resources/soundtrack.mp3")
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play(-1)


        #Screens initiation
        self.menu = MenuScene(self.screen, self.font, self.switch_mode)
        self.credits = CreditsScene(self.screen, self.font, self.switch_mode)

    def run(self):
        while self.running:
            match self.mode:
                case "menu":
                    self.menu.draw()
                case "exit":
                    self.running = False
                case "credits":
                    self.credits.draw()
                case "deck":
                    pass
                case "game":
                    self.show_game(self.game, self.player_id)

            self.handle_pygame_events()
            self.clock.tick(60)
            pygame.display.flip()


    def show_game(self, game, player_id):
        self.screen.fill((30, 30, 30))
        self.draw_text(f"Twój przeciwnik: {game.players[1 - player_id]}", 50, 50)

    def set_game_state(self, game, player_id):
        self.game = game
        self.player_id = player_id

    def switch_mode(self,new_mode):
        self.mode = new_mode

    def handle_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.mode == "menu":
                self.menu.handle_events(event)
            elif self.mode == "credits":
                self.credits.handle_events(event)
            if event.type == pygame.KEYDOWN:
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

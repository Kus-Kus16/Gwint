import pygame

from UI_Classes.CreditsScreen import CreditsScreen
from UI_Classes.MenuScreen import MenuScreen
from UI_Classes.VolumeSlider import VolumeSlider


class PygameView:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800,600))
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
        self.volume_slider = VolumeSlider((self.screen_width - 240, self.screen_height - 60))

        #Screens initiation
        self.menu = MenuScreen(self.screen, self.font, self.switch_mode)
        self.credits = CreditsScreen(self.screen, self.font, self.switch_mode)

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
            #self.volume_slider.draw(self.screen)
            self.clock.tick(60)
            pygame.display.update()


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
            print(f"Event: {event}")  # Logowanie każdego eventu

            # Logowanie pochodzenia zdarzenia
            if event.type == pygame.QUIT:
                print("Quit event triggered")
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                print(f"Mouse clicked at {event.pos}")
                if self.mode == "menu":
                    print("Handling menu")
                    self.menu.handle_events(event)
                elif self.mode == "credits":
                    print("Handling credits")
                    self.credits.handle_events(event)
            elif event.type == pygame.KEYDOWN:
                print(f"Key pressed: {pygame.key.name(event.key)}")
            elif event.type == pygame.MOUSEMOTION:
                print(f"Mouse moved to {event.pos}")
            elif event.type == pygame.ACTIVEEVENT:
                print(f"Window active event: {event.state}")

            # elif event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_RETURN and self.selected_card:
            #         self.locked = True
            #         row = self.selected_card.rows[0]
            #         self.pending_event = {
            #             "type": "card",
            #             "card_id": self.selected_card.id,
            #             "row": row
            #         }

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

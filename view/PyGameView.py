import pygame

from view.Scenes.CreditsScene import CreditsScene
from view.Scenes.GameScene import GameScene
from view.Scenes.MenuScene import MenuScene
from view.Scenes.WaitingScene import WaitingScene
from view.components.VolumeSlider import VolumeSlider


class PygameView:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        #self.screen = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN | pygame.SCALED)
        #self.screen = pygame.display.set_mode((1000,500))
        #self.screen = pygame.display.set_mode((1800,1000))
        #self.screen = pygame.display.set_mode((1280, 720))

        # info = pygame.display.Info()
        # self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN | pygame.SCALED)

        pygame.display.set_caption("Gwint LAN")
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
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        self.volume_slider = VolumeSlider((self.screen_width - 240, self.screen_height - 60))

        #Screens initiation
        self.menu = MenuScene(self.screen, self.font, self.switch_mode)
        self.credits = CreditsScene(self.screen, self.font, self.switch_mode)
        self.waiting = WaitingScene(self.screen, self.font, self.switch_mode)
        self.game_scene = GameScene(self.screen, self.font, self.switch_mode)

    def run(self):
        while self.running:
            self.game_scene.game = self.game
            self.game_scene.player_id = self.player_id

            match self.mode:
                case "menu":
                    self.menu.draw()
                case "exit":
                    self.running = False
                case "credits":
                    self.credits.draw()
                case "deck":
                    pass
                case "waiting-for-game":
                    self.waiting.draw()
                case "start-game":
                    pass
                case "playing":
                    self.game_scene.selected_card = self.selected_card
                    self.game_scene.draw_playing()
                case "waiting":
                    self.game_scene.draw_waiting()
                case "game-over":
                    self.game_scene.draw()
                case "waiting-for-endgame":
                    self.game_scene.draw()
                case _:
                    return

            self.volume_slider.draw(self.screen)
            self.handle_pygame_events()
            self.clock.tick(60)
            pygame.display.flip()



    def set_game_state(self, game, player_id):
        self.game = game
        self.player_id = player_id

    def switch_mode(self,new_mode):
        self.mode = new_mode

    def handle_pygame_events(self):
        for event in pygame.event.get():
            self.volume_slider.handle_event(event)

            if event.type == pygame.QUIT:
                self.running = False

            elif self.mode == "menu":
                self.menu.handle_events(event)
            elif self.mode == "credits":
                self.credits.handle_events(event)
            elif self.mode == "waiting-for-game":
                self.waiting.handle_events(event)

            elif self.mode == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.locked:
                        self.locked = True
                        self.pending_event = {
                            "type": "pass"
                        }

                    elif event.key == pygame.K_RETURN and self.selected_card:
                        if len(self.selected_card.rows) == 1:
                            self.locked = True
                            self.pending_event = {
                                "type": "card",
                                "card_id": self.selected_card.id,
                                "row": self.selected_card.rows[0]
                            }
                            self.selected_card = None  # odznacz kartę

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.locked:
                        for card, rect in self.game_scene.hand_rects:
                            if rect.collidepoint(event.pos):
                                self.selected_card = card
                                return

                        if self.selected_card:
                            for row_name, rect in self.game_scene.row_highlight_rects:
                                if rect.collidepoint(event.pos):
                                    self.locked = True
                                    self.pending_event = {
                                        "type": "card",
                                        "card_id": self.selected_card.id,
                                        "row": row_name
                                    }
                                    self.selected_card = None
                                    return

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


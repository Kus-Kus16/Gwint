import queue

import pygame

from src.view.scenes.settings_scene import SettingsScene
from src.view.scenes.text_scene import TextScene
from src.view.scenes.deck_scene import DeckScene
from src.view.scenes.game_scene import GameScene
from src.view.scenes.menu_scene import MenuScene
from src.presenter import loader as loader, settings
from src.view.constants import ui_constants as u


class PygameView:
    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = self.screen.get_size()
        pygame.display.set_caption("Gwint")

        icon = pygame.image.load(u.ICON_PATH).convert_alpha()
        pygame.display.set_icon(icon)

        self.clock = pygame.time.Clock()
        self.framerate = u.FRAMERATE
        self.show_fps = None
        self.cursor = loader.load_image("resources/ico/cursor.png")

        self.running = True
        self.observer = None
        self.tasks = queue.Queue()

        self.screen_width, self.screen_height = self.screen.get_size()

        # Soundtrack
        pygame.mixer.init()
        pygame.mixer.music.load("resources/soundtrack.mp3")
        pygame.mixer.music.play(-1)

        #Screens initiation
        self.menu = MenuScene(self.screen)
        self.credits = TextScene(self.screen, l("menu.credits"), u.AUTHORS)
        self.waiting = TextScene(self.screen, l("view.waitop")")
        self.game = GameScene(self.screen)
        self.deck = DeckScene(self.screen)
        self.settings = SettingsScene(self.screen)
        self.current_scene = self.menu

        self.on_setting_update()
        settings.register_observer(self, "volume")
        settings.register_observer(self, "show_fps")

    def run(self):
        while self.running:
            self.draw()
            self.handle_tasks()
            self.handle_pygame_events()
            pygame.display.flip()
            self.clock.tick(self.framerate)

    def handle_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.current_scene is not None:
                action = self.current_scene.handle_events(event)
                if action is not None:
                    self.observer.notify(action)

    def handle_tasks(self):
        while not self.tasks.empty():
            task = self.tasks.get()
            task()

    def lock(self):
        self.current_scene.lock()

    def unlock(self):
        self.current_scene.unlock()

    def change_scene(self, scene):
        self.current_scene.clear_temporary()
        self.current_scene.unlock()
        self.current_scene = scene

    def draw(self):
        self.current_scene.draw()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.screen.blit(self.cursor, (mouse_x, mouse_y))

        if not self.show_fps:
            return

        fps = self.clock.get_fps()
        font = pygame.font.SysFont("Arial", 14)
        text_surface = font.render(f"{int(fps)} FPS", True, (0, 255, 0))
        self.screen.blit(text_surface, (2, 2))

    def set_observer(self, observer):
        self.observer = observer

    def run_later(self, runnable):
        self.tasks.put(runnable)

    def notification(self, name, seconds=0, frames=0):
        if frames == 0:
            frames = seconds * self.framerate

        self.current_scene.notification(name, frames, True)

    def on_setting_update(self):
        pygame.mixer.music.set_volume(settings.load_setting("volume"))
        self.show_fps = settings.load_setting("show_fps")
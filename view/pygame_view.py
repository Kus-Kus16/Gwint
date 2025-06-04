import queue

import pygame

from view.scenes.settings_scene import SettingsScene
from view.scenes.text_scene import TextScene
from view.scenes.deck_scene import DeckScene
from view.scenes.game_scene import GameScene
from view.scenes.menu_scene import MenuScene
from view import image_loader as loader, constants as c
from view.components.volume_slider import VolumeSlider


class PygameView:
    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = self.screen.get_size()

        pygame.display.set_caption("Gwint LAN")
        self.clock = pygame.time.Clock()
        self.framerate = c.FRAMERATE
        self.cursor = loader.load_image("resources/ico/cursor.png")
        self.volume_slider = VolumeSlider((self.screen_width - 240, self.screen_height - 60))

        self.running = True
        self.observer = None
        self.tasks = queue.Queue()

        self.screen_width, self.screen_height = self.screen.get_size()

        # Soundtrack
        pygame.mixer.init()
        pygame.mixer.music.load("resources/soundtrack.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        #Screens initiation
        self.menu = MenuScene(self.screen, self.volume_slider)
        self.credits = TextScene(self.screen, c.AUTHORS)
        self.waiting = TextScene(self.screen, ["Oczekiwanie na przeciwnika"])
        self.game = GameScene(self.screen, self.volume_slider)
        self.deck = DeckScene(self.screen)
        self.settings = SettingsScene(self.screen)
        self.current_scene = self.menu

    def run(self):
        while self.running:
            self.draw()
            self.handle_tasks()
            self.handle_pygame_events()
            pygame.display.flip()
            fps = self.clock.get_fps()
            pygame.display.set_caption(f"Gwent LAN - FPS: {fps:.2f}")
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

    def set_observer(self, observer):
        self.observer = observer

    def run_later(self, runnable):
        self.tasks.put(runnable)

    def notification(self, name, seconds=0, frames=0):
        if frames == 0:
            frames = seconds * self.framerate

        self.current_scene.notification(name, frames, True)
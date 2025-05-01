import ctypes
import queue

import pygame

from view.Scenes.CreditsScene import CreditsScene
from view.Scenes.GameScene import GameScene
from view.Scenes.MenuScene import MenuScene
from view.Scenes.WaitingScene import WaitingScene


class PygameView:
    def __init__(self):
        ctypes.windll.user32.SetProcessDPIAware()
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        #self.screen = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN | pygame.SCALED)
        #self.screen = pygame.display.set_mode((1000,500))
        #self.screen = pygame.display.set_mode((1800,1000))
        # self.screen = pygame.display.set_mode((1280, 720))

        # info = pygame.display.Info()
        # self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN | pygame.SCALED)

        pygame.display.set_caption("Gwint LAN")
        self.clock = pygame.time.Clock()
        # self.font = pygame.font.Font("resources/Cinzel/Cinzel-VariableFont_wght.ttf", 30)
        self.font = pygame.font.Font("resources/mason.ttf", 30)
        self.framerate = 60

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
        self.menu = MenuScene(self.screen, self.framerate, self.font)
        self.credits = CreditsScene(self.screen, self.framerate, self.font)
        self.waiting = WaitingScene(self.screen, self.framerate, self.font)
        self.game = GameScene(self.screen, self.framerate, self.font)
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
        self.current_scene.unlock()
        self.current_scene = scene

    def draw(self):
        self.current_scene.draw()

    def set_observer(self, observer):
        self.observer = observer

    def run_later(self, runable):
        self.tasks.put(runable)

    def notification(self, name, seconds=0, frames=0):
        if frames == 0:
            frames = seconds * self.framerate

        self.current_scene.notification(name, frames, True)
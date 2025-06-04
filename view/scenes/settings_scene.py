import pygame

from view.components.button import Button
from view.components.input_box import InputBox
from network.network import Network  # Jeśli chcesz od razu podmieniać IP
from view.scenes.scene import Scene
from view import constants as c

class SettingsScene(Scene):
    def __init__(self, screen):
        super().__init__(screen)
        button_width, button_height = c.BUTTON_SIZE_WIDE

        self.back_button = Button("Powrót do Menu",
                                  ((self.screen_width - button_width) // 2, self.screen_height - button_height - 50),
                                  c.BUTTON_SIZE_WIDE, {"type": "mode_change", "mode": "menu"},
                                  image_paths=c.THEME_BUTTON_PATHS)

        self.input_box = InputBox(self.screen_width // 2 - 100, 200, 200, 40, text="172.20.10.2")
        self.save_ip_button = Button("Zapisz IP",
                                     ((self.screen_width - button_width) // 2, 300),
                                     c.BUTTON_SIZE_WIDE, {"type": "custom", "action": "save_ip"},
                                     image_paths=c.THEME_BUTTON_PATHS)

        self.darken = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.darken.fill((0, 0, 0, 100))

    def draw(self):
        super().draw()
        self.screen.blit(self.darken, (0, 0))
        self.back_button.draw(self.screen, pygame.mouse.get_pos())
        self.save_ip_button.draw(self.screen, pygame.mouse.get_pos())
        self.input_box.draw(self.screen)

    def handle_events(self, event):
        if self.locked:
            return None

        result = self.input_box.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.check_click(event.pos):
                self.lock()
                return self.back_button.action

            if self.save_ip_button.check_click(event.pos):
                new_ip = self.input_box.text.strip()
                from network import network  # Zakładamy, że masz singleton lub instancję
                network.Network().server_ip = new_ip
                network.Network().addr = (new_ip, network.Network().port)
                print("Nowe IP zapisane:", new_ip)

        return None

import pygame

from src.view.components.button import Button
from src.view.components.input_box import InputBox
from src.view import settings
from src.view.scenes.scene import Scene
from src.view.constants import ui_constants as u


class SettingsScene(Scene):
    def __init__(self, screen):
        super().__init__(screen)
        btn_w, btn_h = u.BUTTON_SIZE_WIDE

        # Przyciski
        button_size = u.BUTTON_SIZE_WIDE
        button_paths = u.THEME_BUTTON_PATHS
        self.back_button = Button(
            "Powrót do Menu",
            ((self.screen_width - btn_w) // 2, self.screen_height - btn_h - 50),
            button_size,
            {"type": "mode_change", "mode": "menu"},
            image_paths=button_paths
        )

        self.save_ip_button = Button(
            "Zapisz IP",
            ((self.screen_width - btn_w) // 2, 300),
            button_size,
            {"type": "custom", "action": "save_ip"},
            image_paths=button_paths
        )

        # Pole do wpisania IP
        current_ip = settings.load_setting("ip")
        self.input_box = InputBox(self.screen_width // 2 - 150, 230, 300, 50, text=current_ip)

        # Etykieta
        self.label_font = u.DEFAULT_FONT_BOLD
        self.label_text = "Adres IP serwera:"

    def draw(self):
        super().draw()
        self.draw_overlay(0.85)

        # Rysuj etykietę
        label_surf = self.label_font.render(self.label_text, True, u.COLOR_WHITE)
        label_rect = label_surf.get_rect(center=(self.screen_width // 2, 200))
        self.screen.blit(label_surf, label_rect)

        # Pole input i przyciski
        self.input_box.draw(self.screen)
        self.save_ip_button.draw(self.screen, pygame.mouse.get_pos())
        self.back_button.draw(self.screen, pygame.mouse.get_pos())

    def handle_events(self, event):
        if self.locked:
            return None

        self.input_box.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.check_click(event.pos):
                self.lock()
                return self.back_button.on_click

            if self.save_ip_button.check_click(event.pos):
                new_ip = self.input_box.text.strip()
                return {"type": "mode_change", "mode": "change_ip", "new_ip": new_ip}

        return None

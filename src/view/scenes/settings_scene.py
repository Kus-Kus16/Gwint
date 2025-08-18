import pygame

from src.view.components.button import Button
from src.view.components.input_box import InputBox
from src.presenter import settings
from src.view.components.setting import Setting
from src.view.scenes.scene import Scene
from src.view.constants import ui_constants as u


class SettingsScene(Scene):
    def __init__(self, screen):
        super().__init__(screen)
        btn_w, btn_h = u.BUTTON_SIZE_WIDE

        # Przyciski
        button_size = u.BUTTON_SIZE_WIDE
        button_paths = self.theme_buttons_paths
        self.buttons = [
            Button(
                "Powrót do Menu", ((self.screen_width - btn_w) // 2, self.screen_height - btn_h - 50),
                button_size, {"type": "mode_change", "mode": "menu"}, image_paths=button_paths
            )
        ]

        # Pole do wpisania IP
        current_ip = settings.load_setting("server_ip")

        # Settings
        all_settings = settings.user_settings
        self.settings = [
            Setting("Głośność", (self.screen_width // 4, 200), [f"{i*10}%" for i in range(11)],
                    self.setting_volume, round(all_settings["volume"] * 10), can_wrap=False),
            Setting("Motyw", (self.screen_width // 4, 400), ["Ciri", "Gerald", "Yennefer", "Nithral"],
                    self.setting_theme, all_settings["theme"]),
            Setting("Licznik FPS", (self.screen_width // 4, 600), ["Wył.", "Wł."],
                    self.setting_fps, all_settings["show_fps"]),
            Setting("Język", (3 * self.screen_width // 4, 200), ["PL"],
                    self.setting_language, all_settings["language"]),
            Setting("Szybka gra", (3 * self.screen_width // 4, 400), ["Wył.", "Wł."],
                    self.setting_quickplay, all_settings["quick_play"])
        ]

        self.input_box = InputBox((3 * self.screen_width // 4, 600), u.TEXT_BOX_SIZE,
                                  "IP serwera", self.framerate, self.setting_ip, text=current_ip)

    def draw(self):
        super().draw()
        self.draw_overlay(0.85)
        self.draw_text("Ustawienia", self.screen_width // 2, 100, center=True, font=u.CINZEL_50_BOLD)

        for setting in self.settings:
            setting.draw(self.screen, pygame.mouse.get_pos())

        self.input_box.draw(self.screen)

        for button in self.buttons:
            button.draw(self.screen, pygame.mouse.get_pos())

    def handle_events(self, event):
        if self.locked:
            return

        if self.input_box.handle_events(event):
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for setting in self.settings:
                if setting.handle_events(event):
                    return

            for button in self.buttons:
                if button.check_click(event.pos):
                    self.lock()
                    return button.on_click

        return

    @classmethod
    def setting_volume(cls, setting_index):
        volume = 0.1 * setting_index
        settings.save_setting("volume", volume)

    @classmethod
    def setting_theme(cls, setting_index):
        settings.save_setting("theme", setting_index)

    @classmethod
    def setting_fps(cls, setting_index):
        settings.save_setting("show_fps", setting_index)

    @classmethod
    def setting_language(cls, setting_index):
        settings.save_setting("language", setting_index)

    @classmethod
    def setting_quickplay(cls, setting_index):
        settings.save_setting("quick_play", setting_index)

    @classmethod
    def setting_ip(cls, text):
        settings.save_setting("server_ip", text)
import pygame

from src.view.components.button import Button
from src.view.components.input_box import InputBox
from src.view.components.setting import Setting
from src.view.constants import ui_constants as u
from src.presenter.settings import Settings
from src.view.scenes.scene import Scene


class SettingsScene(Scene):
    def __init__(self, screen):
        super().__init__(screen)
        btn_w, btn_h = u.BUTTON_SIZE_WIDE

        # Przyciski
        button_size = u.BUTTON_SIZE_WIDE
        button_paths = self.theme_buttons_paths
        self.buttons = [
            Button(self.screen, "Return to Menu", ((self.screen_width - btn_w) // 2, self.screen_height - btn_h - 50),
                button_size, {"type": "mode_change", "mode": "menu"}, image_paths=button_paths)
        ]

        # Settings
        self.settings = [
            Setting(self.screen, "Volume", (self.screen_width // 4, 200), [f"{i*10}%" for i in range(11)],
                    self.setting_volume, round(Settings.get_setting("volume") * 10), can_wrap=False),
            Setting(self.screen, "Theme", (self.screen_width // 4, 400), Settings.THEMES,
                    self.setting_theme, Settings.get_setting("theme")),
            Setting(self.screen, "FPS Counter", (self.screen_width // 4, 600), Settings.OFFON,
                    self.setting_fps, Settings.get_setting("show_fps")),
            Setting(self.screen, "Language", (3 * self.screen_width // 4, 200), Settings.LANGUAGES,
                    self.setting_language, Settings.get_setting("language")),
            Setting(self.screen, "Quick Play", (3 * self.screen_width // 4, 400), Settings.OFFON,
                    self.setting_quickplay, Settings.get_setting("quick_play"))
        ]

        current_ip = Settings.get_setting("server_ip")
        self.input_box = InputBox(self.screen, (3 * self.screen_width // 4, 600), u.TEXT_BOX_SIZE,
                                  "Server IP", self.framerate, self.setting_ip, text=current_ip)

    def draw(self):
        super().draw()
        self.draw_overlay(0.85)
        self.draw_text("Settings", self.screen_width // 2, 100, center=True, font=u.CINZEL_50_BOLD)

        for setting in self.settings:
            setting.draw(pygame.mouse.get_pos())

        self.input_box.draw()

        for button in self.buttons:
            button.draw(pygame.mouse.get_pos())

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

    @staticmethod
    def setting_volume(setting_index):
        volume = 0.1 * setting_index
        Settings.save_setting("volume", volume)

    @staticmethod
    def setting_theme(setting_index):
        Settings.save_setting("theme", setting_index)

    @staticmethod
    def setting_fps(setting_index):
        Settings.save_setting("show_fps", setting_index)

    @staticmethod
    def setting_language(setting_index):
        Settings.reload_language(setting_index)
        Settings.save_setting("language", setting_index)

    @staticmethod
    def setting_quickplay(setting_index):
        Settings.save_setting("quick_play", setting_index)

    @staticmethod
    def setting_ip(text):
        Settings.save_setting("server_ip", text)
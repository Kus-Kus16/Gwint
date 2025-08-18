import pygame
from overrides import overrides

from src.view.components.temporary_drawable import TemporaryDrawable
from src.view.constants import ui_constants as u
from src.view.scenes.scene import Scene
from src.view.components.button import Button


class ChooseScene(Scene, TemporaryDrawable):
    def __init__(self, screen):
        Scene.__init__(self, screen)
        TemporaryDrawable.__init__(self, locking=False, frames=-1)

        self.texts = ["Talia Scoia'tael daje ci możliwość podjęcia decyzji,", "kto rozpocznie rozgrywkę jako pierwszy."]
        self.title = "Czy chcesz zacząć jako pierwszy?"

        self.font_title = u.CINZEL_40_BOLD
        self.font_text = u.CINZEL_30
        self.spacing = 30

        button_height = u.BUTTON_SIZE_NARROW[1]
        box_width = 1000
        box_height = 300

        self.box_rect = pygame.Rect(
            (self.screen_width - box_width) // 2,
            (self.screen_height - box_height) // 2,
            box_width,
            box_height,
        )

        total_button_width = 2 * u.BUTTON_SIZE_NARROW[0] + 40
        start_x = self.box_rect.centerx - total_button_width // 2
        y_buttons = self.box_rect.bottom - self.spacing - button_height

        self.buttons = [
            Button("Ja", (start_x, y_buttons), u.BUTTON_SIZE_NARROW, self.button_me),
            Button("Przeciwnik", (start_x + u.BUTTON_SIZE_NARROW[0] + 40, y_buttons), u.BUTTON_SIZE_NARROW,
                   self.button_opp)
        ]

    def draw_box(self):
        spacing = 40

        overlay = pygame.Surface(self.box_rect.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, self.box_rect.topleft)
        pygame.draw.rect(self.screen, u.COLOR_WHITE, self.box_rect, 3, border_radius=5)

        title_surface = self.font_title.render(self.title, True, u.COLOR_LIGHTGRAY)
        title_rect = title_surface.get_rect(center=(self.box_rect.centerx, self.box_rect.top + spacing))
        self.screen.blit(title_surface, title_rect)

        y_pos = self.box_rect.centery - spacing
        for line in self.texts:
            text_surface = self.font_text.render(line, True, u.COLOR_WHITE)
            text_rect = text_surface.get_rect(center=(self.box_rect.centerx, y_pos))
            self.screen.blit(text_surface, text_rect)
            y_pos += spacing

    @overrides
    def draw(self):
        self.draw_overlay(0.60)
        self.draw_box()
        for button in self.buttons:
            button.draw(self.screen, pygame.mouse.get_pos())

    @overrides
    def handle_events(self, event):
        if self.locked:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons:
                if button.check_click(event.pos):
                    return button.on_click()

    def button_me(self):
        self.lock()
        return {
            "type": "first-player",
            "me": True
        }

    def button_opp(self):
        self.lock()
        return {
            "type": "first-player",
            "me": False
        }

    @overrides
    def can_be_handled(self):
        return True
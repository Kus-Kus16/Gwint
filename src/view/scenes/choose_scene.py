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

        self.text = "The Scoia'tael faction perk allows you to decide\nwho will get to go first."
        self.title = "Would you like to go first?"

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
            Button(self.screen, "Me", (start_x, y_buttons), u.BUTTON_SIZE_NARROW, self.button_me),
            Button(self.screen, "Opponent", (start_x + u.BUTTON_SIZE_NARROW[0] + 40, y_buttons), u.BUTTON_SIZE_NARROW,
                   self.button_opp)
        ]

    def draw_box(self):
        spacing = 40

        overlay = pygame.Surface(self.box_rect.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, self.box_rect.topleft)
        pygame.draw.rect(self.screen, u.COLOR_WHITE, self.box_rect, 3, border_radius=5)

        self.draw_text(self.title, self.box_rect.centerx, self.box_rect.top + spacing,
                       color=u.COLOR_LIGHTGRAY, font=self.font_title, center=True)
        self.draw_text(self.text, *self.box_rect.center, font=self.font_text, center=True)

    @overrides
    def draw(self):
        self.draw_overlay(0.60)
        self.draw_box()
        for button in self.buttons:
            button.draw(pygame.mouse.get_pos())

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
import pygame
from overrides import overrides

from src.view.components.temporary_drawable import TemporaryDrawable
from src.view.constants import ui_constants as u
from src.presenter.settings import locale as l
from src.view.components.button import Button
from src.view.constants.ui_constants import COLOR_LIGHTGRAY
from src.view.scenes.scene import Scene


class EndScreen(Scene, TemporaryDrawable):
    def __init__(self, screen, result, round_history):
        Scene.__init__(self, screen)
        TemporaryDrawable.__init__(self, locking=False, frames=-1)

        self.round_history = round_history
        self.image = self.load_ico_image(f"end_{result}")
        self.spacing_frames = u.FRAMERATE // 2

        button_x = self.screen_width // 2
        button_y = self.screen_height - 180
        button_size = u.BUTTON_SIZE
        self.buttons = [
            Button(self.screen, l("Menu"), (button_x - 400, button_y), button_size, self.button_menu),
            Button(self.screen, l("Rematch"), (button_x + 100, button_y), button_size, self.button_rematch),
        ]

    @overrides
    def draw(self):
        if self.spacing_frames >= 0:
            self.spacing_frames -= 1
            if self.spacing_frames == 0:
                self.unlock()

            return

        self.draw_overlay(0.75)

        img_rect = self.image.get_rect(center=(self.screen_width // 2, 280))
        self.screen.blit(self.image, img_rect)

        x_center = self.screen_width // 2
        x_offset = (self.screen_width - 600) // 4
        y = self.screen_height // 2 + 100
        y_offset = 60

        regular = u.CINZEL_30
        bold = u.CINZEL_30_BOLD

        self.draw_text(l("You"), x_center - x_offset, y, color=u.COLOR_GOLD, font=bold, center=True)
        self.draw_text(l("Opponent"), x_center - x_offset, y + y_offset, color=u.COLOR_GOLD, font=bold, center=True)


        for i, text in enumerate([f"{l("Round")} 1", f"{l("Round")} 2", f"{l("Round")} 3"]):
            x = x_center + (i - 1) * x_offset
            self.draw_text(text, x, y - y_offset, color=COLOR_LIGHTGRAY, font=bold, center=True)

            if i < len(self.round_history):
                me_score, opp_score = self.round_history[i]

                if me_score > opp_score:
                    me_color = u.COLOR_GOLD
                    opp_color = u.COLOR_WHITE
                elif opp_score > me_score:
                    me_color = u.COLOR_WHITE
                    opp_color = u.COLOR_GOLD
                else:
                    me_color = opp_color = u.COLOR_WHITE

                me_text = me_score
                opp_text = opp_score
            else:
                me_text = opp_text = "-"
                me_color = opp_color = u.COLOR_WHITE

            self.draw_text(me_text, x, y, color=me_color, font=regular, center=True)
            self.draw_text(opp_text, x, y + y_offset, color=opp_color, font=regular, center=True)

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.draw(mouse_pos)

    @overrides()
    def handle_events(self, event):
        if self.locked:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn.check_click(event.pos):
                    return btn.on_click()

    def button_menu(self):
        self.lock()
        return {
            "type": "game-over",
            "rematch": False
        }

    def button_rematch(self):
        self.lock()
        return {
            "type": "game-over",
            "rematch": True
        }

    @overrides
    def can_be_handled(self):
        return True
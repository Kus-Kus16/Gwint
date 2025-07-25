import pygame
from overrides import overrides

from src.view.constants import ui_constants as u
from src.view.components.button import Button
from src.view.scenes.scene import Scene


class EndScreen(Scene):
    def __init__(self, screen, result, round_history):
        super().__init__(screen)
        self.round_history = round_history
        self.image = self.load_ico_image(f"end_{result}")
        self.spacing_frames = u.FRAMERATE // 2

        button_x = self.screen_width // 2
        button_y = self.screen_height - 180
        button_size = u.BUTTON_SIZE
        self.buttons = [
            Button("Menu", (button_x - 400, button_y), button_size,
                   {"type": "game-over", "rematch": False}),
            Button("Rewanż", (button_x + 100, button_y), button_size,
                   {"type": "game-over", "rematch": True}),
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

        me = bold.render("Ty", True, u.COLOR_GOLD)
        opp = bold.render("Przeciwnik", True, u.COLOR_GOLD)

        me_rect = me.get_rect()
        me_rect.topleft = (x_center - 2 * x_offset, y - me.get_height() // 2)

        opp_rect = opp.get_rect()
        opp_rect.topleft = (x_center - 2 * x_offset, y + y_offset - opp.get_height() // 2)

        self.screen.blit(me, me_rect)
        self.screen.blit(opp, opp_rect)

        for i, text in enumerate(["Runda 1", "Runda 2", "Runda 3"]):
            x = x_center + (i - 1) * x_offset
            label = bold.render(text, True, u.COLOR_LIGHTGRAY)
            label_rect = label.get_rect(center=(x, y - y_offset))
            self.screen.blit(label, label_rect)

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

                me_result = regular.render(str(me_score), True, me_color)
                opp_result = regular.render(str(opp_score), True, opp_color)
            else:
                me_result = regular.render("-", True, u.COLOR_WHITE)
                opp_result = regular.render("-", True, u.COLOR_WHITE)

            me_result_rect = me_result.get_rect(center=(x, y))
            opp_result_rect = opp_result.get_rect(center=(x, y + y_offset))

            self.screen.blit(me_result, me_result_rect)
            self.screen.blit(opp_result, opp_result_rect)

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.draw(self.screen, mouse_pos)

    @overrides()
    def handle_events(self, event):
        if self.locked:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn.check_click(event.pos):
                    self.lock()
                    return btn.action
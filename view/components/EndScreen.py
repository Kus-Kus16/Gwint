import pygame
from overrides import overrides

from view import ImageLoader
from view.Scenes.Scene import Scene
from view.components.Button import Button


def load_image(name):
    path = f"resources/ico/end_{name}.png"
    return ImageLoader.load_image(path)

class EndScreen(Scene):

    def __init__(self, screen, result, round_history, framerate, font=None):
        super().__init__(screen, framerate, font, "resources/board.jpg")
        self.pos = (0, 0)
        self.size = screen.get_size()
        self.rect = pygame.Rect(self.pos, self.size)
        self.round_history = round_history
        self.image = load_image(result)
        self.spacing_frames = framerate // 2

        button_x = self.screen_width // 2
        button_y = self.screen_height - 180
        button_size = (300, 60)
        self.buttons = [
            Button("Menu", (button_x - 400, button_y), button_size,
                   {"type": "mode_change", "mode": "menu"}, font),
            Button("Replay", (button_x + 100, button_y), button_size,
                   {"type": "ui_action", "mode": "menu"}, font),
        ]

    @overrides
    def draw(self):
        if self.spacing_frames >= 0:
            self.spacing_frames -= 1
            if self.spacing_frames == 0:
                self.unlock()

        overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 192))
        self.screen.blit(overlay, self.rect.topleft)

        img_rect = self.image.get_rect(center=(self.screen_width // 2, 280))
        self.screen.blit(self.image, img_rect)

        x_left = 300
        x_offset = (self.screen_width - 600) // 4
        # x_left -= x_offset
        y = self.screen_height // 2 + 100
        y_offset = 60

        self.screen.blit(self.font.render("Ty", True, (197, 152, 79)), (x_left, y))
        self.screen.blit(self.font.render("Przeciwnik", True, (197, 152, 79)), (x_left, y + y_offset))

        for i, text in enumerate(["Runda 1", "Runda 2", "Runda 3"]):
            x = x_left + x_offset * (i + 1)
            label = self.font.render(text, True, (200, 200, 200))
            self.screen.blit(label, (x, y - y_offset))

            if i < len(self.round_history):
                me_score, opp_score = self.round_history[i]

                if me_score > opp_score:
                    me_color = (197, 152, 79)
                    opp_color = (255, 255, 255)
                elif opp_score > me_score:
                    me_color = (255, 255, 255)
                    opp_color = (197, 152, 79)
                else:
                    me_color = opp_color = (255, 255, 255)

                me_result = self.font.render(str(me_score), True, me_color)
                opp_result = self.font.render(str(opp_score), True, opp_color)
            else:
                me_result = self.font.render("-", True, (255, 255, 255))
                opp_result = self.font.render("-", True, (255, 255, 255))

            self.screen.blit(me_result, (x + 25, y))
            self.screen.blit(opp_result, (x + 25, y + y_offset))

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
import pygame

from src.view import loader as loader
from src.view.constants import ui_constants as u


def load_image(name):
    path = f"resources/ico/{name}.png"
    return loader.load_image(path)

class Notification:
    def __init__(self, pos, size, name, frames, locking, font=None):
        self.font = font if font is not None else u.DEFAULT_FONT
        self.rect = pygame.Rect(pos, size)
        self.texts = None
        self.image = None
        self.frames = frames
        self.locking = locking
        self.starting_lock = None
        self.match_name(name)

    def draw(self, screen):
        overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 216))
        screen.blit(overlay, self.rect.topleft)

        screen.blit(self.image, (440, 385))

        line_height = self.font.get_height()
        x = 890
        y_offset = 5
        total_height = len(self.texts) * line_height + (len(self.texts) - 1) * y_offset
        start_y = self.rect.centery - total_height // 2

        for i, line in enumerate(self.texts):
            text_surface = self.font.render(line, True, u.COLOR_GOLD)
            y = start_y + i * (line_height + y_offset)
            screen.blit(text_surface, (x, y))

    def match_name(self, name):
        match name:
            case "playing":
                self.image = load_image("notif_me_turn")
                self.texts = ["Twój ruch!"]
            case "waiting":
                self.image = load_image("notif_op_turn")
                self.texts = ["Ruch przeciwnika"]
            case "start":
                self.image = load_image("notif_me_coin")
                self.texts = ["Zaczynasz jako pierwszy."]
            case "op_start":
                self.image = load_image("notif_op_coin")
                self.texts = ["Przeciwnik zaczyna jako pierwszy."]
            case "round_start":
                self.image = load_image("notif_round_start")
                self.texts = ["Początek rundy"]
            case "pass_op":
                self.image = load_image("notif_round_passed")
                self.texts = ["Przeciwnik spasował"]
            case "pass":
                self.image = load_image("notif_round_passed")
                self.texts = ["Koniec rundy"]
            case "draw_round":
                self.image = load_image("notif_draw_round")
                self.texts = ["Runda zakończyła się remisem."]
            case "lose_round":
                self.image = load_image("notif_lose_round")
                self.texts = ["Przeciwnik wygrał tę rundę."]
            case "win_round":
                self.image = load_image("notif_win_round")
                self.texts = ["Wygrałeś tę rundę!"]
            case _:
                # Texts array
                self.image = load_image("notif_shield")
                self.texts = name

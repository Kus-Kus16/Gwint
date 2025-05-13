import pygame

from view import ImageLoader, Constants as C

def load_image(name):
    path = f"resources/ico/{name}.png"
    return ImageLoader.load_image(path)

class Notification:
    def __init__(self, pos, size, name, frames, locking, font=None):
        self.font = font if font is not None else C.CINZEL_30
        self.rect = pygame.Rect(pos, size)
        self.text = None
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
        text = self.font.render(self.text, True, C.COLOR_GOLD)
        screen.blit(text, (890, self.rect.centery - text.get_height() // 2))


    def match_name(self, name):
        match name:
            case "playing":
                self.image = load_image("notif_me_turn")
                self.text = "Twój ruch!"
            case "waiting":
                self.image = load_image("notif_op_turn")
                self.text = "Ruch przeciwnika"
            case "start":
                self.image = load_image("notif_me_coin")
                self.text = "Zaczynasz jako pierwszy."
            case "op_start":
                self.image = load_image("notif_op_coin")
                self.text = "Przeciwnik zaczyna jako pierwszy."
            case "round_start":
                self.image = load_image("notif_round_start")
                self.text = "Początek rundy"
            case "pass_op":
                self.image = load_image("notif_round_passed")
                self.text = "Przeciwnik spasował"
            case "pass":
                self.image = load_image("notif_round_passed")
                self.text = "Koniec rundy"
            case "draw_round":
                self.image = load_image("notif_draw_round")
                self.text = "Runda zakończyła się remisem."
            case "lose_round":
                self.image = load_image("notif_lose_round")
                self.text = "Przeciwnik wygrał tę rundę."
            case "win_round":
                self.image = load_image("notif_win_round")
                self.text = "Wygrałeś tę rundę!"
            case _:
                self.image = load_image("anim_scorch")

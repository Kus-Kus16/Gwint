import pygame
from overrides import overrides

from src.view import loader as loader
from src.view.components.temporary_drawable import TemporaryDrawable
from src.view.constants import ui_constants as u

notifications = {
    "playing": ("notif_me_turn", ["Twój ruch!"]),
    "waiting": ("notif_op_turn", ["Ruch przeciwnika"]),
    "start": ("notif_me_coin", ["Zaczynasz jako pierwszy."]),
    "op_start": ("notif_op_coin", ["Przeciwnik zaczyna jako pierwszy."]),
    "scoia_start": ("notif_scoiatael", ["Zaczynasz jako pierwszy."]),
    "scoia_op_start": ("notif_scoiatael", ["Przeciwnik zaczyna jako pierwszy."]),
    "op_scoia_start": ("notif_scoiatael", ["Przeciwnik użył zdolności specjalnej talii Scoia'tael,",
                                           "by rozpocząć rozgrywkę jako pierwszy."]),
    "op_scoia_op_start": ("notif_scoiatael", ["Przeciwnik użył zdolności specjalnej talii Scoia'tael,",
                                              "byś rozpoczął rozgrywkę jako pierwszy."]),
    "round_start": ("notif_round_start", ["Początek rundy"]),
    "pass_op": ("notif_round_passed", ["Przeciwnik spasował"]),
    "pass": ("notif_round_passed", ["Koniec rundy"]),
    "draw_round": ("notif_draw_round", ["Runda zakończyła się remisem."]),
    "lose_round": ("notif_lose_round", ["Przeciwnik wygrał tę rundę."]),
    "win_round": ("notif_win_round", ["Wygrałeś tę rundę!"]),
    "north_ability": ("notif_north", ["Dzięki zdolności talii Królestw Północy,",
                                      "po wygranej rundzie dobiera się dodatkową kartę."]),
    "nilfgaard_ability": ("notif_nilfgaard", ["Dzięki zdolności talii Cesarstwa Nilfgaardu,",
                                              "zamiast remisu następuje wygrana Nilfgaardu"]),
    "monsters_ability": ("notif_monsters", ["Dzięki zdolności talii Potworów,",
                                            "losowo wybrana jednostka zostaje do następnej rundy."]),
    "skellige_ability": ("notif_skellige", ["Dzięki zdolności talii Skellige,",
                                            "w trzeciej rundzie dwie losowe karty wracają na stół."]),
    "toussaint_ability": ("notif_toussaint", ["Dzięki zdolności talii Księstwa Toussaint,",
                                              "po przegranej rundzie dobiera się dodatkową kartę."]),
    "fire_ability": ("notif_fire", ["Dzięki zdolności talii Kultu Wiecznego Ognia,",
                                    "na początku rozgrywki wymienia się do czterech kart."]),
}

def load_image(name):
    path = f"resources/ico/{name}.png"
    return loader.load_image(path)

class Notification(TemporaryDrawable):
    def __init__(self, screen, pos, size, name, locking, frames, font=None):
        super().__init__(locking, frames)
        self.screen = screen
        self.font = font if font is not None else u.DEFAULT_FONT
        self.rect = pygame.Rect(pos, size)
        self.texts = None
        self.image = None
        self.match_name(name)

    def draw(self):
        overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 216))
        self.screen.blit(overlay, self.rect.topleft)

        self.screen.blit(self.image, (440, 385))

        line_height = self.font.get_height()
        x = 890
        y_offset = 5
        total_height = len(self.texts) * line_height + (len(self.texts) - 1) * y_offset
        start_y = self.rect.centery - total_height // 2

        for i, line in enumerate(self.texts):
            text_surface = self.font.render(line, True, u.COLOR_GOLD)
            y = start_y + i * (line_height + y_offset)
            self.screen.blit(text_surface, (x, y))

    def match_name(self, name):
        image_name, texts = notifications.get(name, ("notif_shield", name))
        self.image = load_image(image_name)
        self.texts = texts

    @overrides
    def can_be_handled(self):
        return False

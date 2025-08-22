import pygame
from overrides import overrides

from src.presenter import loader as loader
from src.view.components.temporary_drawable import TemporaryDrawable
from src.view.constants import ui_constants as u
from src.presenter.settings import locale as l

def load_image(name):
    path = f"resources/ico/{name}.png"
    return loader.load_image(path)

class Notification(TemporaryDrawable):
    notifications = {
        "me_turn": ("notif_me_turn", [l("Your turn!")]),
        "op_turn": ("notif_op_turn", [l("Opponent's turn")]),
        "start": ("notif_me_coin", [l("You will go first.")]),
        "op_start": ("notif_op_coin", [l("Your opponent will go first.")]),
        "scoia_start": ("notif_scoiatael", [l("You will go first.")]),
        "scoia_op_start": ("notif_scoiatael", [l("Your opponent will go first.")]),
        "op_scoia_start": ("notif_scoiatael", [l("Opponent used the Scoia'tael faction perk"),
                                               l("to go first.")]),
        "op_scoia_op_start": ("notif_scoiatael", [l("Opponent used the Scoia'tael faction perk"),
                                                  l("for you to go first.")]),
        "round_start": ("notif_round_start", [l("Round start")]),
        "pass_op": ("notif_round_passed", [l("Your opponent has passed")]),
        "pass": ("notif_round_passed", [l("Round passed")]),
        "draw_round": ("notif_draw_round", [l("The round ended in a draw.")]),
        "lose_round": ("notif_lose_round", [l("Your opponent won the round.")]),
        "win_round": ("notif_win_round", [l("You won the round!")]),
        "north_ability": ("notif_north", [l("Northern Realms faction ability triggered -"),
                                          l("North draws an additional card.")]),
        "nilfgaard_ability": ("notif_nilfgaard", [l("Nilfgaardian Empire faction ability triggered -"),
                                                  l("Nilfgaard wins the tie.")]),
        "monsters_ability": ("notif_monsters", [l("Monsters faction ability triggered -"),
                                                l("one randomly chosen Monster card stays on board.")]),
        "skellige_ability": ("notif_skellige", [l("Skellige faction ability triggered -"),
                                                l("Two random cards are returned to the board.")]),
        "toussaint_ability": ("notif_toussaint", [l("Duchy of Toussaint faction ability triggered -"),
                                                  l("Toussaint draws an additional card.")]),
        "fire_ability": ("notif_fire", [l("Cult of Eternal Fire faction ability triggered -"),
                                        l("At the beginning of the game, up to four cards are redrawn.")]),
        "waiting": ("notif_round_start", [l("Awaiting your opponent's decision.")])
    }

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
        image_name, texts = self.notifications.get(name, ("notif_shield", name))
        self.image = load_image(image_name)
        self.texts = texts

    @overrides
    def can_be_handled(self):
        return False

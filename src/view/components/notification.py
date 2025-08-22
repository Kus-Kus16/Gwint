import pygame
from overrides import overrides

from src.presenter.loader import Loader
from src.view.components.component import Component
from src.view.components.temporary_drawable import TemporaryDrawable
from src.view.constants import ui_constants as u
from src.presenter.settings import locale as l

class Notification(Component, TemporaryDrawable):
    notifications = {
        "me_turn": ("notif_me_turn", l("Your turn!")),
        "op_turn": ("notif_op_turn", l("Opponent's turn")),
        "start": ("notif_me_coin", l("You will go first.")),
        "op_start": ("notif_op_coin", l("Your opponent will go first.")),
        "scoia_start": ("notif_scoiatael", l("You will go first.")),
        "scoia_op_start": ("notif_scoiatael", l("Your opponent will go first.")),
        "op_scoia_start": ("notif_scoiatael", l("Opponent used the Scoia'tael faction perk\nto go first.")),
        "op_scoia_op_start": ("notif_scoiatael", l("Opponent used the Scoia'tael faction perk\nfor you to go first.")),
        "round_start": ("notif_round_start", l("Round start")),
        "pass_op": ("notif_round_passed", l("Your opponent has passed")),
        "pass": ("notif_round_passed", l("Round passed")),
        "draw_round": ("notif_draw_round", l("The round ended in a draw.")),
        "lose_round": ("notif_lose_round", l("Your opponent won the round.")),
        "win_round": ("notif_win_round", l("You won the round!")),
        "north_ability": ("notif_north",
                          l("Northern Realms faction ability triggered -\nNorth draws an additional card.")),
        "nilfgaard_ability": ("notif_nilfgaard",
                             l("Nilfgaardian Empire faction ability triggered -\nNilfgaard wins the tie.")),
        "monsters_ability": ("notif_monsters",
                            l("Monsters faction ability triggered -\none randomly chosen Monster card stays on board.")),
        "skellige_ability": ("notif_skellige",
                             l("Skellige faction ability triggered -\nTwo random cards are returned to the board.")),
        "toussaint_ability": ("notif_toussaint",
                              l("Duchy of Toussaint faction ability triggered -\nToussaint draws an additional card.")),
        "fire_ability": ("notif_fire",
                         l("Cult of Eternal Fire faction ability triggered -\nat the beginning of the game, up to four cards are redrawn.")),
        "waiting": ("notif_round_start", l("Awaiting your opponent's decision."))
    }

    def __init__(self, screen, pos, size, name, locking, frames, font=None):
        TemporaryDrawable.__init__(self, locking, frames)
        Component.__init__(self, screen)
        self.font = font if font is not None else u.DEFAULT_FONT
        self.rect = pygame.Rect(pos, size)
        self.text = None
        self.image = None
        self.match_name(name)

    def draw(self):
        overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 216))
        self.screen.blit(overlay, self.rect.topleft)

        self.screen.blit(self.image, (440, 385))

        x, y = 890, self.rect.centery
        self.draw_text(self.text, x, y, u.COLOR_GOLD, self.font)

    def match_name(self, name):
        image_name, text = self.notifications.get(name, ("notif_shield", name))
        self.image = self.load_image(image_name)
        self.text = text

    @staticmethod
    def load_image(name):
        path = f"resources/ico/{name}.png"
        return Loader.load_image(path)

    @overrides
    def can_be_handled(self):
        return False

    @overrides
    def _draw_text_lines(self, lines, x, y, color=u.COLOR_WHITE, font0=u.CINZEL_30, font1=None, spacing=30, center=False):
        super()._draw_text_lines(lines, x, y, color, font0, spacing=5)
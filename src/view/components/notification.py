import pygame
from overrides import overrides

from src.presenter import loader as loader
from src.view.components.temporary_drawable import TemporaryDrawable
from src.view.constants import ui_constants as u

notifications = {
    "me_turn": ("notif_me_turn", [l("notif.yourturn")]),
    "op_turn": ("notif_op_turn", [l("notif.opturn")]),
    "start": ("notif_me_coin", [l("notif.yourcoin")]),
    "op_start": ("notif_op_coin", [l("notif.opcoin")]),
    "scoia_start": ("notif_scoiatael", [l("notif.youcoin")]),
    "scoia_op_start": ("notif_scoiatael", [l("notif.opcoin")]),
    "op_scoia_start": ("notif_scoiatael", [l("notif.specscoi"),
                                           l("notif.startfirst1")]),
    "op_scoia_op_start": ("notif_scoiatael", [l("notif.specscoi"),
                                              l("notif.startfirst2")]),
    "round_start": ("notif_round_start", [l("notif.roundstart")]),
    "pass_op": ("notif_round_passed", [l("notif.oppassed")]),
    "pass": ("notif_round_passed", [l("notif.roundend")]),
    "draw_round": ("notif_draw_round", [l("notif.rounddraw")]),
    "lose_round": ("notif_lose_round", [l("notif.opwon")]),
    "win_round": ("notif_win_round", [l("notif.youwon")]),
    "north_ability": ("notif_north", [f"{l("notif.thankstal" {l("notif.kingdom")})}",
                                      l("notif.afterround")]),
    "nilfgaard_ability": ("notif_nilfgaard", [f"{l("notif.thankstal")} {l("notif.empire")}",
                                              l("notif.insteaempire")]),
    "monsters_ability": ("notif_monsters", [f"{l("notif.thankstal")} {l("notif.monsters")}",
                                            l("notif.randomnextround")]),
    "skellige_ability": ("notif_skellige", [f"{l("notif.thankstal")} {l("notif.island")}",
                                            l("notif.thirdround")]),
    "toussaint_ability": ("notif_toussaint", [f"{l("notif.thankstal")} {l("notif.principality")}",
                                              l("notif.addcard")]),
    "fire_ability": ("notif_fire", [f"{l("notif.thankstal")} {l("notif.cult")}",
                                    l("notif.change4cards")]),
    "waiting": ("notif_round_start", [l("notif.opwait")])
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

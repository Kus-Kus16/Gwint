from overrides import overrides

from src.model.abilities.commanders.find_base import FindBase
from src.model.enums.row_type import RowType


class FindFlame(FindBase):
    def __init__(self, card):
        super().__init__(card, 332)

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        super().on_board_play(game, player, RowType.CLOSE, targets)
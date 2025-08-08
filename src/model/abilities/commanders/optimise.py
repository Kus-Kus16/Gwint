from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase
from src.model.enums.row_type import RowType


class Optimise(CommanderAbilityBase):
    @overrides
    def on_board_play(self, game, player, row_type, targets):
        row, _ = game.board.get_row(RowType.CLOSE, player.id)
        for card in row.cards:
            print(card)
        return
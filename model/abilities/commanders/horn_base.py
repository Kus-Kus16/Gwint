from abc import ABC

from overrides import overrides

from model.abilities.commanders.commander_base import CommanderAbilityBase


class HornBase(CommanderAbilityBase, ABC):
    def __init__(self, card, row_type):
        super().__init__(card)
        self.row_type = row_type

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        row, _ = game.board.get_row(self.row_type, player.id)
        if not row.add_horn(self.card):
            raise ValueError(f"Wrong commander use: cannot add horn for row {row_type}")
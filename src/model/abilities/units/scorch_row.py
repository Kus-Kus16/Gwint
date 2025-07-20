from overrides import overrides

from src.model.abilities.units.unit_base import UnitAbilityBase


class ScorchRow(UnitAbilityBase):
    @overrides
    def on_board_play(self, game, player, row_type, targets):
        actions = [lambda: self.scorch_row(game, player, row_type)]
        return actions

    @classmethod
    def scorch_row(cls, game, player, row_type):
        opponent_id = 1 - player.id
        scorched = game.board.scorch_row(row_type, opponent_id)
        game.grave_cards(scorched)
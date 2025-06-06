from abc import ABC

from overrides import overrides

from model.abilities.commanders.commander_base import CommanderAbilityBase


class ScorchBase(CommanderAbilityBase, ABC):
    def __init__(self, card, row_type):
        super().__init__(card)
        self.row_type = row_type

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        opponent_id = 1 - player.id
        scorched = game.board.scorch_row(self.row_type, opponent_id)
        game.grave_cards(scorched)
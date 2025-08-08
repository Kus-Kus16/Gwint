from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase


class ScorchEnemyLow(CommanderAbilityBase):
    @overrides
    def on_board_play(self, game, player, row_type, targets):
        opponent_id = 1 - player.id
        scorched = game.board.scorch_low(opponent_id)
        game.grave_cards(scorched)
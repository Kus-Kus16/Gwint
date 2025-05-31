from overrides import overrides

from model.abilities.commanders.commander_base import CommanderAbilityBase


class ShowEnemy(CommanderAbilityBase):
    @overrides
    def on_board_play(self, game, player, row_type, targets):
        opponent_id = 1 - player.id
        shown = game.peek_cards(opponent_id, 3)
        return shown
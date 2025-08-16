from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase


class SwapMorale(CommanderAbilityBase):
    @overrides
    def on_board_play(self, game, player, row_type, targets):
        player.rules["swap_morale"] = True
        player.commander.disable()
        game.board.update_rows()

    @overrides
    def on_round_end(self, game, player):
        player.rules["swap_morale"] = False
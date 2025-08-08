from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase


class Optimise(CommanderAbilityBase):
    @overrides
    def on_board_play(self, game, player, row_type, targets):
        #TODO doxlarise
        return
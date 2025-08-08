from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase
from src.model.abilities.specials import decoy as special_decoy
from src.model.enums.ability_type import AbilityType


class FindDecoy(CommanderAbilityBase):
    @overrides
    def get_types(self):
        return [AbilityType.TARGETING]

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        card = player.get_from_deck(1)
        if card is None:
            return

        special_decoy.decoy(game, player, row_type, targets, card, "commander")
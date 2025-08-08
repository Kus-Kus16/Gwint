from overrides import overrides

from src.model.abilities.specials.special_base import SpecialAbilityBase
from src.model.enums.ability_type import AbilityType
from src.model.abilities.units import mardroeme as unit_mardroeme


class Mardroeme(SpecialAbilityBase):
    @overrides
    def get_types(self):
        return [AbilityType.BOOST]

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        unit_mardroeme.mardroeme(game, player, row_type, self.card)
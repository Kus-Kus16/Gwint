from overrides import overrides

from model.abilities.specials.special_base import SpecialAbilityBase
from model.abilities.units import scorch as unit_scorch
from model.enums.ability_type import AbilityType


class Scorch(SpecialAbilityBase):
    @overrides
    def get_types(self):
        return [AbilityType.ABSOLUTE]

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        unit_scorch.scorch(game)
        self.card.send_to_owner_grave()
from overrides import overrides

from model.abilities.units.unit_base import UnitAbilityBase
from model.enums.ability_type import AbilityType


class Recall(UnitAbilityBase):
    @overrides
    def get_types(self):
        return [AbilityType.RECALLING]
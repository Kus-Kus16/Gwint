from overrides import overrides

from model.abilities.ability_base import AbilityType
from model.abilities.units.unit_base import UnitAbilityBase


class Avenge(UnitAbilityBase):
    @overrides
    def get_types(self):
        return [AbilityType.AVENGING]
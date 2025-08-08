from overrides import overrides

from src.model.abilities.units.unit_base import UnitAbilityBase
from src.model.enums.ability_type import AbilityType


class Thirsty(UnitAbilityBase):
    @overrides
    def get_types(self):
        return [AbilityType.THIRSTY]
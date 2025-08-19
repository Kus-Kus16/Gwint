from overrides import overrides

from src.model.abilities.units.unit_base import UnitAbilityBase
from src.model.enums.ability_type import AbilityType

class LowMorale(UnitAbilityBase):
    @overrides
    def get_types(self):
        return [AbilityType.DEMORALIZING]

    @overrides
    def on_row_insert(self, row):
        row.effects["low_morale"].add(self.card)

    @overrides
    def on_row_remove(self, row):
        row.effects["low_morale"].remove(self.card)
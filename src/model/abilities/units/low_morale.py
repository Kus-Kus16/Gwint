from overrides import overrides

from src.model.abilities.units.unit_base import UnitAbilityBase


class LowMorale(UnitAbilityBase):
    @overrides
    def on_row_insert(self, row):
        row.effects["low_morale"].add(self.card)

    @overrides
    def on_row_remove(self, row):
        row.effects["low_morale"].remove(self.card)
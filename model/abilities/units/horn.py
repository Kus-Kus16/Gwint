from overrides import overrides

from model.abilities.units.unit_base import UnitAbilityBase


class Horn(UnitAbilityBase):
    @overrides
    def on_row_insert(self, row):
        row.effects["horn"].add(self.card)

    @overrides
    def on_row_remove(self, row):
        row.effects["horn"].remove(self.card)
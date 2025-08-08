from overrides import overrides

from src.model.abilities.units.unit_base import UnitAbilityBase
from src.model.enums.ability_type import AbilityType
from src.model.cards import cards_database as db


class Berserker(UnitAbilityBase):
    @overrides
    def get_types(self):
        return [AbilityType.BERSERK]

    @overrides
    def on_row_insert(self, row):
        if row.effects["mardroeme"]:
            extra = db.get_berserker(self.card.id)
            extra.owner = self.card.owner
            row.add_card(extra)
            row.remove_card(self.card)
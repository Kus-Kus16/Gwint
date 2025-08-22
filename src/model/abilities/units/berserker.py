from overrides import overrides

from src.model.abilities.units.unit_base import UnitAbilityBase
from src.model.enums.ability_type import AbilityType
from src.model.cards.cards_database import CardsDatabase


class Berserker(UnitAbilityBase):
    @overrides
    def get_types(self):
        return [AbilityType.BERSERK]

    @overrides
    def on_row_insert(self, row):
        if row.effects["mardroeme"]:
            extra = CardsDatabase.get_berserker_card(self.card.id)
            extra.owner = self.card.owner
            row.add_card(extra)
            row.remove_card(self.card)
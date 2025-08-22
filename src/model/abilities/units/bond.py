from overrides import overrides

from src.model.cards.cards_database import CardsDatabase
from src.model.abilities.units.unit_base import UnitAbilityBase
from src.model.enums.ability_type import AbilityType


class Bond(UnitAbilityBase):
    def __init__(self, card):
        super().__init__(card)
        self.bond_id = CardsDatabase.get_bond(self.card.id)

    @overrides
    def get_types(self):
        return [AbilityType.BONDING]

    @overrides
    def on_row_insert(self, row):
        row.effects["bond"].setdefault(self.bond_id, 0)
        row.effects["bond"][self.bond_id] += 1

    @overrides
    def on_row_remove(self, row):
        row.effects["bond"][self.bond_id] -= 1
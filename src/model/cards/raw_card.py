from abc import ABC

from src.model.cards.card_base import CardBase
from src.model.enums.card_type import CardType
from src.model.enums.row_type import RowType

class RawCard(CardBase, ABC):
    def __init__(self, data):
        super().__init__(data)
        self.base_power = data['power']
        self.power = self.base_power
        self.rows = self.create_rows(data["rows"])
        self.type = (
            CardType.SPECIAL if self.power is None
            else CardType.HERO if "hero" in data['abilities']
            else CardType.UNIT
        )

    @classmethod
    def create_rows(cls, strings):
        rows = []
        for row_name in strings:
            rows.append(RowType[row_name.upper()])

        return rows

    def __lt__(self, other):
        if self.is_card_type(CardType.SPECIAL) and not other.is_card_type(CardType.SPECIAL):
            return True
        if not self.is_card_type(CardType.SPECIAL) and other.is_card_type(CardType.SPECIAL):
            return False

        if self.power != other.power:
            return self.power < other.power

        return self.id < other.id

    def __gt__(self, other):
        if self.is_card_type(CardType.SPECIAL) and not other.is_card_type(CardType.SPECIAL):
            return False
        if not self.is_card_type(CardType.SPECIAL) and other.is_card_type(CardType.SPECIAL):
            return True

        if self.power != other.power:
            return self.power > other.power

        return self.id > other.id
from overrides import overrides

from model.card_base import CardBase, CardType


class Card(CardBase):
    def __init__(self, data):
        super().__init__(data)
        self.base_power = data['power']
        self.power = self.base_power
        self.rows = data['rows']
        self.type = (
            CardType.SPECIAL if self.power is None
            else CardType.HERO if "hero" in self.abilities
            else CardType.UNIT
        )

    def set_power(self, power):
        if self.is_hero() or self.is_special():
            return

        self.power = power

    def reset_power(self):
        self.power = self.base_power

    @overrides
    def is_row_playable(self, row_type):
        if self.is_special():
            return True

        for row in self.rows:
            if row.upper() == row_type.name:
                return True

        return False

    def send_to_owner_grave(self):
        self.owner.send_to_grave(self)

    def __lt__(self, other):
        if self.is_special() and not other.is_special():
            return True
        if not self.is_special() and other.is_special():
            return False

        if self.power != other.power:
            return self.power < other.power

        return self.id < other.id

    def __gt__(self, other):
        if self.is_special() and not other.is_special():
            return False
        if not self.is_special() and other.is_special():
            return True

        if self.power != other.power:
            return self.power > other.power

        return self.id > other.id

    def __str__(self):
        return f'{self.id} {self.name} {self.power}'
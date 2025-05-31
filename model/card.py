from overrides import overrides

from model.card_base import CardBase, CardType


class Card(CardBase):
    def __init__(self, data):
        super().__init__(data)
        self.base_power = data['power']
        self.power = self.base_power
        self.rows = data['rows'] #TODO change from strings
        self.type = (
            CardType.SPECIAL if self.power is None
            else CardType.HERO if "hero" in data['abilities']
            else CardType.UNIT
        )

        path = f"abilities.{'specials' if self.type is CardType.SPECIAL else 'units'}"
        self.abilities = self.create_abilities(data['abilities'], path)

    def set_power(self, power):
        if self.is_card_type(CardType.HERO) or self.is_card_type(CardType.SPECIAL):
            return

        self.power = power

    def reset_power(self):
        self.power = self.base_power

    @overrides
    def is_row_playable(self, row_type):
        if self.is_card_type(CardType.SPECIAL):
            return True

        for row in self.rows:
            if row.upper() == row_type.name:
                return True

        return False

    def send_to_owner_grave(self):
        self.owner.send_to_grave(self)

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

    def __str__(self):
        return f'{self.id} {self.name} {self.power}'
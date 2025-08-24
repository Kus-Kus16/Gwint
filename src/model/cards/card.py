from overrides import overrides

from src.model.cards.raw_card import RawCard
from src.model.enums.card_type import CardType

class Card(RawCard):
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

        for row_t in self.rows:
            if row_t == row_type:
                return True

        return False

    def send_to_owner_grave(self):
        self.owner.send_to_grave(self)
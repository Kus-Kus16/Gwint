from classes.CardHolder import CardHolder
from enum import Enum
import bisect


class RowType(Enum):
    CLOSE = 0
    RANGED = 1
    SIEGE = 2

class Row(CardHolder):
    def __init__(self):
        super().__init__()
        self.points = 0

    def add_card(self, card):
        bisect.insort(self.cards, card)

    def recalculate(self):
        self.points = 0
        #TODO add power changes
        for card in self.cards:
            self.points += card.power

        return self.points

    def __str__(self):
        return str(self.points) + " :: " + ", ".join(str(card) for card in self.cards)
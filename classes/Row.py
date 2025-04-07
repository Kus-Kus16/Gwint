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
        self.effects = {"weather": False}

    def add_card(self, card):
        bisect.insort(self.cards, card)

    def recalculate(self):
        #TODO add power changes
        total = 0

        for card in self.cards:
            self.apply_effects(card)
            total += card.power

        self.points = total
        return total

    def apply_effects(self, card):
        if card.is_hero():
            return

        if self.effects["weather"]:
            card.power = min(card.power, 1)
        else:
            card.power = card.base_power

    def add_weather(self):
        self.effects["weather"] = True
        self.recalculate()

    def clear_weather(self):
        self.effects["weather"] = False
        self.recalculate()

    ## TODO CHANGE HERE AFTER ABILITIES!
    # def transfer_card(self, card, container):
    #     super.transfer_card(card, container)
    #
    # def transfer_all_cards(self, container):
    #     super.transfer_all_cards(container)

    def __str__(self):
        return str(self.points) + " :: " + ", ".join(str(card) for card in self.cards)
from classes.CardHolder import CardHolder
from enum import Enum
import bisect


class RowType(Enum):
    CLOSE = 0
    RANGED = 1
    SIEGE = 2
    CLOSE_OPP = 3
    RANGED_OPP = 4
    SIEGE_OPP = 5

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

    def find_strongest(self):
        maxi = -10e10
        for card in self.cards:
            if card.power > maxi:
                maxi = card.power

        return self.find_cards(lambda card: card.power == maxi)

    def find_weakest(self):
        maxi = 10e10
        for card in self.cards:
            if card.power > maxi:
                maxi = card.power

        return self.find_cards(lambda card: card.power == maxi)

    ## TODO CHANGE HERE AFTER ABILITIES!
    # def transfer_card(self, card, container):
    #     super.transfer_card(card, container)
    #
    # def transfer_all_cards(self, container):
    #     super.transfer_all_cards(container)

    def __str__(self):
        return str(self.points) + " :: " + ", ".join(str(card) for card in self.cards)
from classes.CardHolder import CardHolder

import bisect

class Hand(CardHolder):
    def __init__(self):
        super().__init__()

    def add_card(self, card):
        bisect.insort(self.cards, card)
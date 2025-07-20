from src.model.card_holders.card_holder import CardHolder

import bisect

class Hand(CardHolder):
    def add_card(self, card):
        bisect.insort(self.cards, card)
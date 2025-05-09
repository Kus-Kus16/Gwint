from classes.CardHolder import CardHolder

import bisect

class Hand(CardHolder):

    def add_card(self, card):
        bisect.insort(self.cards, card)
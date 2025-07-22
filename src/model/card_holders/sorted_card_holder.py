import bisect

from src.model.card_holders.card_holder import CardHolder


class SortedCardHolder(CardHolder):
    def add_card(self, card):
        bisect.insort(self.cards, card)
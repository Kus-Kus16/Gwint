from classes.CardHolder import CardHolder
import random

class Deck(CardHolder):
    def __init__(self, cards):
        super().__init__(cards)
        self.shuffle()

    def own_cards(self, owner):
        for card in self.cards:
            card.owner = owner

    def shuffle(self):
        random.shuffle(self.cards)

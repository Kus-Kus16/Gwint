from classes.CardHolder import CardHolder

class Deck(CardHolder):
    def __init__(self, cards):
        super().__init__(cards)

    def own_cards(self, owner):
        for card in self.cards:
            card.owner = owner

    def shuffle(self, rng):
        rng.shuffle(self.cards)
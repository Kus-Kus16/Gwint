from model.card_holders.card_holder import CardHolder

class Deck(CardHolder):
    def own_cards(self, owner):
        for card in self.cards:
            card.owner = owner

    def shuffle(self, rng):
        rng.shuffle(self.cards)
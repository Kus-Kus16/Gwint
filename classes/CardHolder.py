import random

class CardHolder:
    def __init__(self, cards=None):
        if cards is None:
            cards = []

        random.shuffle(cards)
        self.cards = cards

    def size(self):
        return len(self.cards)

    def add_card(self, card):
        self.cards.append(card)

    def remove_card(self, card):
        self.cards.remove(card)

    def find_card(self, predicate):
        for card in self.cards:
            if predicate(card):
                return card

    def find_card_by_id(self, card_id):
        return self.find_card(lambda card: card.id == card_id)

    def find_card_by_name(self, card_name):
        return self.find_card(lambda card: card.name == card_name)

    def get_next_card(self):
        if len(self.cards) == 0:
            return None

        return self.cards.pop(0)

    def __str__(self):
        return "\n".join(str(card) for card in self.cards)
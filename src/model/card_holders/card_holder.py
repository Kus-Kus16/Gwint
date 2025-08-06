from abc import ABC


class CardHolder(ABC):
    def __init__(self, cards=None):
        if cards is None:
            cards = []

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

    def find_cards(self, predicate):
        cards = []
        for card in self.cards:
            if predicate(card):
                cards.append(card)

        return cards

    def find_card_by_id(self, card_id):
        return self.find_card(lambda card: card.id == card_id)

    def find_card_by_name(self, card_name):
        return self.find_card(lambda card: card.name == card_name)

    def get_card(self, predicate):
        for card in self.cards:
            if predicate(card):
                self.remove_card(card)
                return card

    def get_card_by_id(self, card_id):
        return self.get_card(lambda card: card.id == card_id)

    def get_next_card(self):
        if len(self.cards) == 0:
            return None

        return self.cards.pop(0)
    
    def transfer_card(self, card, container):
        self.remove_card(card)
        container.add_card(card)

    def transfer_all_cards(self, container):
        for card in list(self.cards):
            self.transfer_card(card, container)

    def filter_cards(self, ability_type):
        filtered = [card for card in self.cards if card.is_ability_type(ability_type)]
        return filtered
from src.model.cards import cards_database as db
from src.model.cards.raw_card import RawCard

class CardEntry(RawCard):
    def __init__(self, data):
        super().__init__(data)
        self.count = data['count']

    def copy(self, count):
        card_data = db.find_card_by_id(self.id)
        card = CardEntry(card_data)
        card.count = count
        return card

    def dump(self):
        return {'id': self.id, 'count': self.count}
from model.card_base import CardBase, CardType


class Commander(CardBase):
    def __init__(self, data):
        super().__init__(data)
        self.nickname = data['nickname']
        self.type = CardType.COMMANDER
        self.active = True
        self.filename = data['filename']

    def is_row_playable(self, row_type):
        return True

    def disable(self):
        self.active = False

    def enable(self):
        self.active = True

    def ability(self):
        return self.abilities[0]
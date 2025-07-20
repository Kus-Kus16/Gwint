from src.model.card_base import CardBase
from src.model.enums.card_type import CardType


class Commander(CardBase):
    def __init__(self, data):
        super().__init__(data)
        self.nickname = data['nickname']
        self.type = CardType.COMMANDER
        self.active = True
        self.abilities = self.create_abilities(data['abilities'], "abilities.commanders")

    def disable(self):
        self.active = False

    def enable(self):
        self.active = True

    def ability(self):
        return self.abilities[0]
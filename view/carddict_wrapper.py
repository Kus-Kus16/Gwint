from model.enums.card_type import CardType


class CardDictWrapper:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.faction = data.get('faction')
        self.filename = data.get('filename')
        self.power = data.get('power')
        self.base_power = self.power
        self.type = (
            CardType.SPECIAL if self.power is None
            else CardType.HERO if "hero" in data.get('abilities')
            else CardType.UNIT
        )

    def is_card_type(self, card_type):
        return self.type == card_type
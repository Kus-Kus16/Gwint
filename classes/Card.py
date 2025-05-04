from enum import Enum

class CardType(Enum):
    SPECIAL = 0
    UNIT = 1
    HERO = 2
    COMMANDER = 3

class Card:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.faction = data['faction']
        self.base_power = data['power']
        self.power = self.base_power
        self.owner = None
        self.rows = data['rows']
        self.abilities = data['abilities']
        self.filename = data['filename']
        self.type = (
            CardType.SPECIAL if self.power is None
            else CardType.HERO if "hero" in self.abilities
            else CardType.UNIT
        )

    def is_unit(self):
        return self.type == CardType.UNIT

    def is_hero(self):
        return self.type == CardType.HERO

    def is_special(self):
        return self.type == CardType.SPECIAL

    def is_weather(self):
        if not self.type == CardType.SPECIAL:
            return False

        return any(ability in self.abilities for ability in ["frost", "fog", "rain", "storm", "clear"])

    def is_boost(self):
        if not self.type == CardType.SPECIAL:
            return False

        return any(ability in self.abilities for ability in ["horn", "mardroeme", "sangreal"])

    def is_targeting(self):
        if not self.type == CardType.SPECIAL:
            return False

        return any(ability in self.abilities for ability in ["decoy"])

    def is_absolute(self):
        if not self.type == CardType.SPECIAL:
            return False

        return any(ability in self.abilities for ability in ["scorch"])

    def set_power(self, power):
        if self.is_hero() or self.is_special():
            return

        self.power = power

    def reset_power(self):
        self.power = self.base_power

    def is_row_playable(self, row_type):
        if self.is_special():
            return True

        for row in self.rows:
            if row.upper() == row_type.name:
                return True

        return False

    def send_to_owner_grave(self):
        self.owner.send_to_grave(self)

    def __lt__(self, other):
        if self.is_special() and not other.is_special():
            return True
        if not self.is_special() and other.is_special():
            return False

        if self.power != other.power:
            return self.power < other.power

        return self.id < other.id

    def __gt__(self, other):
        if self.is_special() and not other.is_special():
            return False
        if not self.is_special() and other.is_special():
            return True

        if self.power != other.power:
            return self.power > other.power

        return self.id > other.id

    def __str__(self):
        return f'{self.id} {self.name} {self.power}'

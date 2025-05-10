from abc import ABC, abstractmethod
from enum import Enum

class CardType(Enum):
    SPECIAL = 0
    UNIT = 1
    HERO = 2
    COMMANDER = 3

class CardBase(ABC):
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.faction = data['faction']
        self.owner = None
        self.filename = data['filename']
        self.abilities = data['abilities']
        self.type = None

    def is_unit(self):
        return self.type == CardType.UNIT

    def is_hero(self):
        return self.type == CardType.HERO

    def is_special(self):
        return self.type == CardType.SPECIAL

    def is_commander(self):
        return self.type == CardType.COMMANDER

    def is_weather(self):
        if not self.is_special():
            return False

        return any(ability in self.abilities for ability in ["frost", "fog", "rain", "storm", "clear"])

    def is_boost(self):
        if not self.is_special():
            return False

        return any(ability in self.abilities for ability in ["horn", "mardroeme", "sangreal"])

    def is_targeting(self):
        if not self.is_special():
            return False

        return any(ability in self.abilities for ability in ["decoy"])

    def is_choosing(self):
        return any(ability in self.abilities for ability in ["medic", "chooseEnemyGrave"])

    def is_recalling(self):
        return any(ability in self.abilities for ability in ["recall"])

    def is_avenging(self):
        return any(ability in self.abilities for ability in ["avenger"])

    def is_absolute(self):
        if self.is_commander():
            return True

        if not self.is_special():
            return False

        return any(ability in self.abilities for ability in ["scorch"])

    @abstractmethod
    def is_row_playable(self, row_type):
        pass
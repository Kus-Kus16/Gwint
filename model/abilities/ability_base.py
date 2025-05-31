from abc import ABC
from enum import Enum


class AbilityType(Enum):
    WEATHER = 0
    BOOST = 1
    TARGETING = 2
    CHOOSING = 3
    RECALLING = 4
    AVENGING = 5
    ABSOLUTE = 6
    BONDING = 7

class AbilityBase(ABC):
    def __init__(self, card):
        self.card = card
        self.__apply_type()

    def on_board_play(self, game, player, row_type, targets):
        return []

    def on_row_insert(self, row):
        return

    def on_row_remove(self, row):
        return

    def on_carousel_request(self, presenter):
        return []

    def get_types(self):
        return []

    def __apply_type(self):
        types = self.get_types()
        self.card.add_types(types)
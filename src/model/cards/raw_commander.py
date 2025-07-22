from abc import ABC

from src.model.cards.card_base import CardBase
from src.model.enums.card_type import CardType

class RawCommander(CardBase, ABC):
    def __init__(self, data):
        super().__init__(data)
        self.type = CardType.COMMANDER
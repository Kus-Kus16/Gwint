from model.abilities.commanders.horn_base import HornBase
from model.card_holders.row import RowType


class HornSiege(HornBase):
    def __init__(self, card):
        super().__init__(card, RowType.SIEGE)
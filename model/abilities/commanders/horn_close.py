from model.abilities.commanders.horn_base import HornBase
from model.enums.row_type import RowType


class HornClose(HornBase):
    def __init__(self, card):
        super().__init__(card, RowType.CLOSE)
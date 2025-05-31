from model.abilities.commanders.scorch_base import ScorchBase
from model.card_holders.row import RowType


class ScorchClose(ScorchBase):
    def __init__(self, card):
        super().__init__(card, RowType.CLOSE)
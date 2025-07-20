from src.model.abilities.commanders.scorch_base import ScorchBase
from src.model.enums.row_type import RowType


class ScorchRanged(ScorchBase):
    def __init__(self, card):
        super().__init__(card, RowType.RANGED)
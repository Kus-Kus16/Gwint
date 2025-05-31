from overrides import overrides

from model.abilities.specials.weather_base import WeatherBase, WeatherType
from model.card_holders.row import RowType


class Frost(WeatherBase):
    def __init__(self, card):
        super().__init__(card, WeatherType.FROST)

    @overrides
    def get_affected_rows(self):
        return [RowType.CLOSE, RowType.CLOSE_OPP]
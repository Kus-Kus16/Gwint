from overrides import overrides

from model.abilities.specials.weather_base import WeatherBase, WeatherType
from model.card_holders.row import RowType


class Rain(WeatherBase):
    def __init__(self, card):
        super().__init__(card, WeatherType.RAIN)

    @overrides
    def get_affected_rows(self):
        return [RowType.SIEGE, RowType.SIEGE_OPP]
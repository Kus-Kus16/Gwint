from overrides import overrides

from model.abilities.specials.weather_base import WeatherBase
from model.enums.row_type import RowType
from model.enums.weather_type import WeatherType


class Frost(WeatherBase):
    def __init__(self, card):
        super().__init__(card, WeatherType.FROST)

    @overrides
    def get_affected_rows(self):
        return [RowType.CLOSE, RowType.CLOSE_OPP]
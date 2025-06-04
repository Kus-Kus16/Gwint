from overrides import overrides

from model.abilities.specials.weather_base import WeatherBase
from model.enums.weather_type import WeatherType


class Clear(WeatherBase):
    def __init__(self, card):
        super().__init__(card, WeatherType.CLEAR)

    @overrides
    def get_affected_rows(self):
        return []
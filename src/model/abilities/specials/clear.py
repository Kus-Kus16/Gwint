from overrides import overrides

from src.model.abilities.specials.weather_base import WeatherBase
from src.model.enums.weather_type import WeatherType


class Clear(WeatherBase):
    def __init__(self, card):
        super().__init__(card, WeatherType.CLEAR)

    @overrides
    def get_affected_rows(self):
        return []
from overrides import overrides

from src.model.abilities.specials.weather_base import WeatherBase
from src.model.enums.row_type import RowType
from src.model.enums.weather_type import WeatherType


class Fog(WeatherBase):
    def __init__(self, card):
        super().__init__(card, WeatherType.FOG)

    @overrides
    def get_affected_rows(self):
        return [RowType.RANGED, RowType.RANGED_OPP]
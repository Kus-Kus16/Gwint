from abc import ABC, abstractmethod
from overrides import overrides

from src.model.abilities.specials.special_base import SpecialAbilityBase
from src.model.enums.ability_type import AbilityType


class WeatherBase(SpecialAbilityBase, ABC):
    def __init__(self, card, weather_type):
        super().__init__(card)
        self.weather_type = weather_type

    @overrides
    def get_types(self):
        return [AbilityType.WEATHER]

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        if game.board.is_weather_active(self.weather_type):
            self.card.send_to_owner_grave()
        else:
            game.board.add_weather(self.card, self, player.id)

    @abstractmethod
    def get_affected_rows(self):
        pass
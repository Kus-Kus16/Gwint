from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase


class WeatherHalf(CommanderAbilityBase):
    @overrides
    def on_start_game(self, game, player):
        player.rules["weather_half"] = True
        player.commander.disable()
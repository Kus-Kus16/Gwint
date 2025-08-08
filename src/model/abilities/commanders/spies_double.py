from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase


class SpiesDouble(CommanderAbilityBase):
    @overrides
    def on_start_game(self, game, player):
        game.gamerules["spies_double"] = True
        player.commander.disable()
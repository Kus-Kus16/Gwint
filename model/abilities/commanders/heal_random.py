from overrides import overrides

from model.abilities.commanders.commander_base import CommanderAbilityBase


class HealRandom(CommanderAbilityBase):
    @overrides
    def on_start_game(self, game, player):
        game.gamerules["heal_random"] = True
        player.commander.disable()
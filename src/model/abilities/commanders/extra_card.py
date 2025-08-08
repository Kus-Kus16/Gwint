from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase


class ExtraCard(CommanderAbilityBase):
    @overrides
    def on_start_game(self, game, player):
        player.draw_card()
        player.commander.disable()
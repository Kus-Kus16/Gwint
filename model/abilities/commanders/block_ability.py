from overrides import overrides

from model.abilities.commanders.commander_base import CommanderAbilityBase


class BlockAbility(CommanderAbilityBase):
    @overrides
    def on_start_game(self, game, player):
        opponent = game.get_player(1 - player.id)
        player.commander.disable()
        opponent.commander.disable()
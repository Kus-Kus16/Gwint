from abc import ABC

from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase


class GameruleBase(CommanderAbilityBase, ABC):
    def __init__(self, card, gamerule):
        super().__init__(card)
        self.gamerule = gamerule

    @overrides
    def on_start_game(self, game, player):
        game.gamerules[self.gamerule] = True
        player.commander.disable()
from overrides import overrides

from model.abilities.ability_base import AbilityBase, AbilityType


class CommanderAbilityBase(AbilityBase):
    @overrides
    def get_types(self):
        return [AbilityType.ABSOLUTE]

    def on_start_game(self, game, player):
        return
from abc import ABC

from overrides import overrides

from src.model.abilities.ability_base import AbilityBase
from src.model.enums.ability_type import AbilityType


class CommanderAbilityBase(AbilityBase, ABC):
    @overrides
    def get_types(self):
        return [AbilityType.ABSOLUTE]

    def on_start_game(self, game, player):
        return
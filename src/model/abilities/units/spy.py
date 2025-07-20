from overrides import overrides

from src.model.abilities.units.unit_base import UnitAbilityBase


class Spy(UnitAbilityBase):
    @overrides
    def on_board_play(self, game, player, row_type, targets):
        actions = [lambda: self.spy(player)]
        return actions

    @classmethod
    def spy(cls, player):
        player.draw_cards(2)
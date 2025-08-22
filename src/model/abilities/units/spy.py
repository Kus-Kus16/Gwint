from overrides import overrides

from src.model.abilities.units.unit_base import UnitAbilityBase


class Spy(UnitAbilityBase):
    def __init__(self, card):
        super().__init__(card)
        self.double_power = False

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        self.double_power = game.gamerule("spies_double")
        actions = [lambda: self.spy(player)]
        return actions

    @staticmethod
    def spy(player):
        player.draw_cards(2)

    @overrides
    def on_power_recalculate(self):
        if self.double_power:
            self.card.power *= 2
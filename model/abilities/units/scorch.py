from overrides import overrides

from model.abilities.units.unit_base import UnitAbilityBase


def scorch(game):
    scorched = game.board.scorch()
    game.grave_cards(scorched)

class Scorch(UnitAbilityBase):
    @overrides
    def on_board_play(self, game, player, row_type, targets):
        actions = [lambda: scorch(game)]
        return actions

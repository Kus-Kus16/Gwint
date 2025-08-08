from overrides import overrides

from src.model.abilities.units.unit_base import UnitAbilityBase


def mardroeme(game, player, row_type, card):
    player_id = player.id
    row, row_owner_id = game.board.get_row(row_type, player_id)

    if row_owner_id != player_id:
        raise ValueError(f"Wrong mardroeme use: row_owner_id:{row_owner_id} does not match p{player_id}")
    if not row.add_mardroeme(card):
        raise ValueError(f"Wrong mardroeme use: cannot add for row {row_type}")

class Mardroeme(UnitAbilityBase):
    @overrides
    def on_board_play(self, game, player, row_type, targets):
        actions = [lambda: mardroeme(game, player, row_type, self.card)]
        return actions
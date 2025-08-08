from overrides import overrides

from src.model.abilities.units.unit_base import UnitAbilityBase


def sangreal(game, player, row_type, card):
    player_id = player.id
    row, row_owner_id = game.board.get_row(row_type, player_id)

    if row_owner_id != player_id:
        raise ValueError(f"Wrong sangreal use: row_owner_id:{row_owner_id} does not match p{player_id}")
    if not row.add_sangreal(card):
        raise ValueError(f"Wrong sangreal use: cannot add for row {row_type}")

class Sangreal(UnitAbilityBase):
    @overrides
    def on_board_play(self, game, player, row_type, targets):
        actions = [lambda: sangreal(game, player, row_type, self.card)]
        return actions